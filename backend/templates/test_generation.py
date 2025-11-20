import os
import shutil
import json
from PIL import Image
from django.test import TestCase, override_settings
from django.conf import settings
from .models import Template
from .generator import SiteGenerator
from .engine import VariableContext, substitute_variables

@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_gen_test'))
class SiteGeneratorTest(TestCase):
    def setUp(self):
        self.test_dir = settings.MEDIA_ROOT
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create a dummy template
        self.template = Template.objects.create(
            name="Gen Test",
            type="MONOLITHIC",
            content="<html><body class='main-body'><div class='content'>{{CONTENT}}</div><img src='assets/logo.png'></body></html>",
            config={"variables": ["CONTENT"]}
        )
        
        # Create dummy assets
        self.assets_dir = os.path.join(self.test_dir, 'templates', 'gen-test', 'assets')
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Create a dummy CSS file
        with open(os.path.join(self.assets_dir, 'style.css'), 'w') as f:
            f.write(".main-body { color: red; } .content { padding: 10px; }")
            
        # Create a dummy Image
        img = Image.new('RGB', (500, 500), color='red')
        img.save(os.path.join(self.assets_dir, 'logo.png'))

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_variable_substitution(self):
        site_data = {'brand_name': 'TestBrand'}
        page_data = {'content_html': '<p>Hello World</p>'}
        context = VariableContext(site_data, page_data)
        
        content = "{{SITE_BRAND}} says {{CONTENT}}"
        result = substitute_variables(content, context)
        self.assertEqual(result, "TestBrand says <p>Hello World</p>")

    def test_site_generation_full_flow(self):
        # Mock Site object
        class MockSite:
            id = 123
            brand_name = "My Site"
            domain = "example.com"
            pages = [{'slug': 'index', 'title': 'Home', 'content_html': '<h1>Welcome</h1>'}]
            
        site = MockSite()
        
        # Configure fingerprinting
        fingerprint_config = {
            'footprint_type': 'WORDPRESS'
        }
        
        generator = SiteGenerator(site, self.template.id, fingerprint_config)
        zip_path = generator.generate()
        
        self.assertTrue(os.path.exists(zip_path))
        
        # Verify Build Content
        build_dir = generator.build_dir
        
        # 1. Check HTML generation
        with open(os.path.join(build_dir, 'index.html'), 'r') as f:
            html = f.read()
            
        # Check variable substitution
        self.assertIn("<h1>Welcome</h1>", html)
        
        # Check CMS Footprint (WordPress path)
        # The original HTML had src='assets/logo.png'
        # It should be remapped to wp-content/themes/default/assets/logo.png
        self.assertIn("wp-content/themes/default/assets/logo.png", html)
        
        # Check CSS Class Randomization
        # 'main-body' and 'content' should be replaced by random strings like '_xxxxx_xxxxx'
        self.assertNotIn("class='main-body'", html)
        self.assertRegex(html, r"class='_[a-z0-9]{5}_[a-z0-9]{5}'")
        
        # 2. Check Assets
        # Check CSS file content
        css_path = os.path.join(build_dir, 'assets', 'style.css')
        with open(css_path, 'r') as f:
            css = f.read()
            
        self.assertNotIn(".main-body", css)
        self.assertRegex(css, r"\._[a-z0-9]{5}_[a-z0-9]{5}")
        
        # Check Image Processing
        img_path = os.path.join(build_dir, 'assets', 'logo.png')
        with Image.open(img_path) as img:
            # Original was 500x500. New one should be slightly different (0.98 to 1.02 variation)
            width, height = img.size
            self.assertNotEqual(width, 500) # Should have changed
            self.assertTrue(490 <= width <= 510)
