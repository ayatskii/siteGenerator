import os
import shutil
import uuid
import zipfile
from django.conf import settings
from .models import Template
from .engine import VariableContext, render_template
from .fingerprinting import CSSRandomizer, FootprintManager
from .image_processing import ImageFingerprinter

class SiteGenerator:
    def __init__(self, site, template_id, fingerprint_config=None):
        self.site = site
        self.template = Template.objects.get(id=template_id)
        self.fingerprint_config = fingerprint_config or {}
        self.build_id = str(uuid.uuid4())
        self.build_dir = os.path.join(settings.MEDIA_ROOT, 'builds', self.build_id)
        
        # Fingerprinting tools
        seed = str(site.id) # Deterministic seed based on site ID
        self.css_randomizer = CSSRandomizer(seed)
        self.image_fingerprinter = ImageFingerprinter(seed)
        
        # Determine footprint type
        footprint_type = self.fingerprint_config.get('footprint_type', 'CUSTOM')
        self.footprint_manager = FootprintManager(footprint_type)

    def generate(self):
        """
        Orchestrates the site generation process.
        """
        try:
            os.makedirs(self.build_dir, exist_ok=True)
            
            # 1. Prepare Assets
            self._prepare_assets()
            
            # 2. Fingerprint Assets
            self._fingerprint_assets()
            
            # 3. Render Pages
            self._render_pages()
            
            # 4. Package
            output_zip = self._package_site()
            
            return output_zip
            
        finally:
            # Cleanup build dir
            # shutil.rmtree(self.build_dir) # Commented out for debugging
            pass

    def _prepare_assets(self):
        """
        Copies template assets to the build directory.
        """
        # Source assets from template storage
        # Assuming template assets are stored in media/templates/<slug>/assets/
        # We need a way to get the real path. For now, let's assume a standard path structure.
        # In a real app, the Template model might store the path.
        
        # Quick fix: derive path from template name/slug logic used in upload service
        slug = self.template.name.lower().replace(' ', '-')
        source_assets = os.path.join(settings.MEDIA_ROOT, 'templates', slug, 'assets')
        
        target_assets = os.path.join(self.build_dir, 'assets')
        
        if os.path.exists(source_assets):
            shutil.copytree(source_assets, target_assets)

    def _fingerprint_assets(self):
        """
        Applies fingerprinting to CSS and Images.
        """
        assets_dir = os.path.join(self.build_dir, 'assets')
        if not os.path.exists(assets_dir):
            return

        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                # CSS Randomization
                if ext == '.css':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Generate map (accumulative if multiple CSS files)
                    self.css_randomizer.generate_class_map(content)
                    
                    # Apply map to CSS itself
                    new_content = self.css_randomizer.apply_class_map(content, is_css=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                
                # Image Fingerprinting
                elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    self.image_fingerprinter.process_image(file_path, file_path)

    def _render_pages(self):
        """
        Renders all pages for the site.
        """
        # Mocking pages for now since we don't have the Page model fully integrated in this context
        # In real implementation: pages = self.site.pages.all()
        
        # For this task, we'll assume self.site has a method or property to get pages
        # Or we'll just render a dummy index page if no pages found
        
        pages = getattr(self.site, 'pages', [])
        if not pages:
            # Create a dummy page for testing
            pages = [{'title': 'Home', 'slug': 'index', 'content_html': '<p>Welcome</p>'}]

        for page in pages:
            # Build Context
            # We need to convert the page object to a dict if it's a model
            page_data = page if isinstance(page, dict) else page.__dict__
            site_data = self.site if isinstance(self.site, dict) else self.site.__dict__
            
            context = VariableContext(site_data, page_data)
            
            # Render Template
            html_content = render_template(self.template, context)
            
            # Apply Fingerprinting to HTML
            # 1. CSS Classes
            html_content = self.css_randomizer.apply_class_map(html_content, is_css=False)
            
            # 2. CMS Footprints (Path remapping)
            html_content = self.footprint_manager.remap_paths(html_content)
            
            # Save to file
            filename = 'index.html' if page_data.get('slug') == 'index' else f"{page_data.get('slug')}.html"
            with open(os.path.join(self.build_dir, filename), 'w', encoding='utf-8') as f:
                f.write(html_content)

    def _package_site(self):
        """
        Zips the generated site.
        """
        zip_filename = f"{self.build_id}.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, 'builds', zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.build_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.build_dir)
                    zipf.write(file_path, arcname)
                    
        return zip_path
