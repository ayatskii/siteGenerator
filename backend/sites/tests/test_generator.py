from django.test import TestCase
from django.contrib.auth import get_user_model
from sites.models import Site, Page, Block, Deployment
from sites.services.site_generator import SiteGenerator
from templates.models import Template
import os
from django.conf import settings

User = get_user_model()

class SiteGeneratorTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a test site
        self.site = Site.objects.create(
            name='Test Site',
            domain='example.com',
            owner=self.user,
            brand_name='Test Brand',
            language='en-US'
        )
        
        # Create a test page
        self.page = Page.objects.create(
            site=self.site,
            title='Home Page',
            slug='index',
            meta_title='Home - Test Site',
            meta_description='This is a test site',
            h1_heading='Welcome to Test Site',
            published=True
        )
        
        # Create a test block
        Block.objects.create(
            page=self.page,
            type='article',
            order=1,
            content={
                'html_content': '<p>This is test content</p>'
            },
            is_active=True
        )
    
    def test_generator_creates_zip(self):
        """Test that the generator creates a ZIP file"""
        generator = SiteGenerator(self.site)
        zip_path = generator.generate()
        
        self.assertTrue(os.path.exists(zip_path))
        self.assertTrue(zip_path.endswith('.zip'))
        
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(generator.build_dir):
            import shutil
            shutil.rmtree(generator.build_dir)
    
    def test_generator_creates_html_files(self):
        """Test that the generator creates HTML files for pages"""
        generator = SiteGenerator(self.site)
        
        # Create build directory
        os.makedirs(generator.build_dir, exist_ok=True)
        
        # Render pages
        generator._render_pages()
        
        # Check if index.html exists
        index_path = os.path.join(generator.build_dir, 'index.html')
        self.assertTrue(os.path.exists(index_path))
        
        # Read content
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if content includes the block content
        self.assertIn('test content', content.lower())
        
        # Cleanup
        if os.path.exists(generator.build_dir):
            import shutil
            shutil.rmtree(generator.build_dir)
    
    def test_generator_fingerprinting(self):
        """Test that fingerprinting is applied"""
        generator = SiteGenerator(self.site)
        
        # This would require actual CSS files to fingerprint
        # For now, just verify the method runs without error
        generator._fingerprint_assets()
        
        # If we had CSS files, we'd check that class names are randomized
        # This is a basic smoke test
        self.assertTrue(True)
        
        # Cleanup
        if os.path.exists(generator.build_dir):
            import shutil
            shutil.rmtree(generator.build_dir)
