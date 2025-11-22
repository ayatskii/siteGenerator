from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from sites.models import Site, Page, Block, SwiperPreset

User = get_user_model()

class BlockTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.site = Site.objects.create(owner=self.user, name='Test Site', domain='test.com')
        self.page = Page.objects.create(site=self.site, title='Test Page', slug='test-page')

    def test_create_hero_block(self):
        data = {
            'page': self.page.id,
            'type': 'hero',
            'order': 1,
            'content': {
                'headline': 'Welcome',
                'subheading': 'To my site',
                'cta_buttons': [{'text': 'Click Me', 'link': '#'}]
            }
        }
        response = self.client.post('/api/sites/blocks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Block.objects.count(), 1)

    def test_create_empty_article_block(self):
        # Empty content should be allowed for initial state
        data = {
            'page': self.page.id,
            'type': 'article',
            'order': 2,
            'content': {}
        }
        response = self.client.post('/api/sites/blocks/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Block.objects.count(), 1)

    def test_reorder_blocks(self):
        b1 = Block.objects.create(page=self.page, type='hero', order=1, content={})
        b2 = Block.objects.create(page=self.page, type='article', order=2, content={})
        
        data = {
            'blocks': [
                {'id': b1.id, 'order': 2},
                {'id': b2.id, 'order': 1}
            ]
        }
        response = self.client.post('/api/sites/blocks/reorder/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        b1.refresh_from_db()
        b2.refresh_from_db()
        self.assertEqual(b1.order, 2)
        self.assertEqual(b2.order, 1)

    def test_page_duplication_with_blocks(self):
        Block.objects.create(page=self.page, type='hero', order=1, content={'headline': 'Original'})
        
        response = self.client.post(f'/api/sites/pages/{self.page.id}/duplicate/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_page_id = response.data['id']
        new_page = Page.objects.get(id=new_page_id)
        
        self.assertEqual(new_page.blocks.count(), 1)
        self.assertEqual(new_page.blocks.first().content['headline'], 'Original')
        self.assertNotEqual(new_page.blocks.first().id, self.page.blocks.first().id)

class SwiperPresetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.site = Site.objects.create(owner=self.user, name='Test Site', domain='test.com')

    def test_create_swiper_preset(self):
        data = {
            'site': self.site.id,
            'name': 'My Preset',
            'items': [{'image': 'img1.jpg', 'title': 'Slide 1'}],
            'button_text': 'Play Now'
        }
        response = self.client.post('/api/sites/swiper-presets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SwiperPreset.objects.count(), 1)
