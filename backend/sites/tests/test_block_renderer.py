from django.test import TestCase
from sites.services.block_renderer import BlockRenderer

class BlockRendererTests(TestCase):
    def test_render_hero(self):
        content = {
            'headline': 'Test Headline',
            'subheading': 'Test Subheading',
            'image_url': 'http://example.com/image.jpg',
            'cta_buttons': [{'text': 'Click Me', 'link': '#'}]
        }
        html = BlockRenderer.render_hero(content)
        self.assertIn('Test Headline', html)
        self.assertIn('Test Subheading', html)
        self.assertIn('http://example.com/image.jpg', html)
        self.assertIn('Click Me', html)

    def test_render_article(self):
        content = {
            'html_content': '<p>Test Content</p>',
            'use_article_tag': True
        }
        html = BlockRenderer.render_article(content)
        self.assertIn('<article>', html)
        self.assertIn('<p>Test Content</p>', html)

    def test_render_image(self):
        content = {
            'image_url': 'http://example.com/image.jpg',
            'alt_text': 'Alt Text'
        }
        html = BlockRenderer.render_image(content)
        self.assertIn('src="http://example.com/image.jpg"', html)
        self.assertIn('alt="Alt Text"', html)

    def test_render_faq(self):
        content = {
            'title': 'FAQ Title',
            'items': [{'question': 'Q1', 'answer': 'A1'}]
        }
        html = BlockRenderer.render_faq(content)
        self.assertIn('FAQ Title', html)
        self.assertIn('Q1', html)
        self.assertIn('A1', html)
