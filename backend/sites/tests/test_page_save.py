from django.test import TestCase
from django.contrib.auth import get_user_model
from sites.models import Site, Page, Block
from sites.services.page_service import PageService

User = get_user_model()

class PageSaveTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.site = Site.objects.create(owner=self.user, name='Test Site', domain='test.com')
        self.page = Page.objects.create(site=self.site, title='Test Page', slug='test-page')

    def test_save_page_content(self):
        data = {
            'title': 'Updated Title',
            'blocks': [
                {
                    'type': 'hero',
                    'content': {'headline': 'New Hero'}
                },
                {
                    'type': 'article',
                    'content': {'html_content': '<p>New Article</p>'}
                }
            ]
        }
        
        updated_page = PageService.save_page_content(self.page, data)
        
        self.assertEqual(updated_page.title, 'Updated Title')
        self.assertEqual(updated_page.blocks.count(), 2)
        self.assertEqual(updated_page.blocks.first().type, 'hero')
        self.assertEqual(updated_page.blocks.last().type, 'article')

    def test_update_existing_block(self):
        block = Block.objects.create(page=self.page, type='hero', content={'headline': 'Old Hero'}, order=0)
        
        data = {
            'blocks': [
                {
                    'id': block.id,
                    'type': 'hero',
                    'content': {'headline': 'Updated Hero'}
                }
            ]
        }
        
        PageService.save_page_content(self.page, data)
        block.refresh_from_db()
        self.assertEqual(block.content['headline'], 'Updated Hero')

    def test_delete_missing_blocks(self):
        block1 = Block.objects.create(page=self.page, type='hero', order=0)
        block2 = Block.objects.create(page=self.page, type='article', order=1)
        
        data = {
            'blocks': [
                {
                    'id': block1.id,
                    'type': 'hero',
                    'content': {}
                }
            ]
        }
        
        PageService.save_page_content(self.page, data)
        self.assertEqual(self.page.blocks.count(), 1)
        self.assertTrue(Block.objects.filter(id=block1.id).exists())
        self.assertFalse(Block.objects.filter(id=block2.id).exists())
