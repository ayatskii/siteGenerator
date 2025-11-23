import os
import json
import shutil
import zipfile
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Template, TemplateSection

class TemplateUploadService:
    def __init__(self, zip_file, name=None, description=None):
        self.zip_file = zip_file
        self.name_override = name
        self.description_override = description
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(uuid.uuid4()))
        self.template_slug = None

    def process(self):
        try:
            self._extract_zip()
            self._validate_structure()
            config = self._read_config()
            
            # Apply overrides
            if self.name_override:
                config['name'] = self.name_override
            if self.description_override:
                config['description'] = self.description_override
                
            self.template_slug = self._slugify(config['name'])
            
            with transaction.atomic():
                # 1. Handle Assets
                asset_prefix = self._handle_assets()
                
                # 2. Create Records
                if config['type'] == 'MONOLITHIC':
                    self._create_monolithic(config, asset_prefix)
                elif config['type'] == 'SECTIONAL':
                    self._create_sectional(config, asset_prefix)
                else:
                    raise ValidationError(f"Unknown template type: {config.get('type')}")
                
        finally:
            self._cleanup()

    def _extract_zip(self):
        os.makedirs(self.temp_dir, exist_ok=True)
        try:
            with zipfile.ZipFile(self.zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
        except zipfile.BadZipFile:
            raise ValidationError("Invalid ZIP file")

    def _validate_structure(self):
        if not os.path.exists(os.path.join(self.temp_dir, 'config.json')):
            raise ValidationError("Missing config.json")
        
        # Security check for assets
        assets_path = os.path.join(self.temp_dir, 'assets')
        if os.path.exists(assets_path):
            for root, dirs, files in os.walk(assets_path):
                for file in files:
                    if file.lower().endswith(('.php', '.py', '.exe', '.sh')):
                        raise ValidationError(f"Forbidden file type in assets: {file}")

    def _read_config(self):
        try:
            with open(os.path.join(self.temp_dir, 'config.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValidationError("Invalid config.json format")

    def _handle_assets(self):
        source_assets = os.path.join(self.temp_dir, 'assets')
        if not os.path.exists(source_assets):
            return ""

        target_dir = os.path.join(settings.MEDIA_ROOT, 'templates', self.template_slug, 'assets')
        
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        shutil.copytree(source_assets, target_dir)
        
        # Return the URL prefix for assets
        return f"{settings.MEDIA_URL}templates/{self.template_slug}/assets/"

    def _create_monolithic(self, config, asset_prefix):
        index_path = os.path.join(self.temp_dir, 'index.html')
        if not os.path.exists(index_path):
            raise ValidationError("Missing index.html for Monolithic template")

        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Rewrite asset paths
        if asset_prefix:
            content = content.replace('assets/', asset_prefix)

        Template.objects.create(
            name=config['name'],
            type='MONOLITHIC',
            description=config.get('description', ''),
            content=content,
            config=config,
            fingerprint_config=config.get('fingerprint', {}),
            available_variables=config.get('variables', [])
        )

    def _create_sectional(self, config, asset_prefix):
        base_path = os.path.join(self.temp_dir, 'base.html')
        if not os.path.exists(base_path):
            raise ValidationError("Missing base.html for Sectional template")

        with open(base_path, 'r', encoding='utf-8') as f:
            base_content = f.read()

        if asset_prefix:
            base_content = base_content.replace('assets/', asset_prefix)

        template = Template.objects.create(
            name=config['name'],
            type='SECTIONAL',
            description=config.get('description', ''),
            content=base_content, # Storing wrapper in content
            config=config,
            fingerprint_config=config.get('fingerprint', {}),
            available_variables=config.get('variables', [])
        )

        sections_dir = os.path.join(self.temp_dir, 'sections')
        if not os.path.exists(sections_dir):
            raise ValidationError("Missing sections directory")

        for section_conf in config.get('sections', []):
            file_path = os.path.join(self.temp_dir, section_conf['file'])
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    section_content = f.read()
                
                if asset_prefix:
                    section_content = section_content.replace('assets/', asset_prefix)

                TemplateSection.objects.create(
                    template=template,
                    name=section_conf['name'],
                    content=section_content,
                    order=section_conf.get('order', 0),
                    is_required=section_conf.get('required', False)
                )

    def _cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _slugify(self, text):
        return text.lower().replace(' ', '-')
