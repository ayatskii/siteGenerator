from django.test import TestCase
from django.contrib.auth import get_user_model
from sites.models import Site, Page, Block
from templates.models import Template
from sites.services.page_service import PageService

User = get_user_model()

class PagePreviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.template = Template.objects.create(
            name='Test Template', 
            type='MONOLITHIC', 
            content='<html><body>{{CONTENT}}</body></html>'
        )
        self.site = Site.objects.create(
            owner=self.user, 
            name='Test Site', 
            domain='test.com',
            template=self.template
        )
        self.page = Page.objects.create(site=self.site, title='Test Page', slug='test-page')
        Block.objects.create(
            page=self.page, 
            type='article', 
            content={'html_content': '<p>Preview Content</p>'},
            order=0
        )

    def test_generate_preview(self):
        html = PageService.generate_preview(self.page)
        self.assertIn('<html><body>', html)
        self.assertIn('<p>Preview Content</p>', html)
        self.assertIn('</body></html>', html)
