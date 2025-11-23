from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import TextPrompt
from tokens.models import APIToken
from sites.models import Site, Page, Block
from .services import AIService
from unittest.mock import patch, MagicMock

User = get_user_model()

class AIServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token = APIToken.objects.create(
            name='Test Token',
            service_type='openai',
            token_value='sk-test-token',
            ai_model='gpt-3.5-turbo',
            created_by=self.user
        )
        self.prompt = TextPrompt.objects.create(
            name='Test Prompt',
            target_type='article',
            template='Write an article about {{keywords}} for {{brand}}.',
            ai_model='gpt-3.5-turbo',
            created_by=self.user
        )

    def test_variable_substitution(self):
        service = AIService()
        context = {'keywords': 'AI', 'brand': 'TechCorp'}
        result = service.substitute_variables(self.prompt.template, context)
        self.assertEqual(result, 'Write an article about AI for TechCorp.')

    @patch('requests.post')
    def test_generate_content_openai(self, mock_post):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Generated Content'}}]
        }
        mock_post.return_value = mock_response

        service = AIService()
        context = {'keywords': 'AI', 'brand': 'TechCorp'}
        
        result = service.generate_content(self.prompt.id, context)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['content'], 'Generated Content')
        
        # Verify usage incremented
        self.token.refresh_from_db()
        self.assertEqual(self.token.current_usage, 1)

class PromptAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.site = Site.objects.create(owner=self.user, name='Test Site', domain='test.com')
        self.page = Page.objects.create(site=self.site, title='Test Page', slug='test-page')
        
        self.prompt = TextPrompt.objects.create(
            name='Test Prompt',
            target_type='article',
            template='Test Template',
            created_by=self.user
        )
        
        # Need a token for generation to work (mocked)
        self.token = APIToken.objects.create(
            name='Test Token',
            service_type='openai',
            token_value='sk-test',
            ai_model='gpt-3.5-turbo',
            created_by=self.user
        )

    def test_list_prompts(self):
        response = self.client.get('/api/prompts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('prompts.services.AIService.generate_content')
    def test_generate_content_endpoint(self, mock_generate):
        mock_generate.return_value = {'success': True, 'content': 'Generated via API'}
        
        data = {
            'prompt_id': self.prompt.id,
            'page_id': self.page.id,
            'extra_context': {'custom': 'value'}
        }
        
        response = self.client.post('/api/prompts/generate/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Generated via API')
        mock_generate.assert_called_once()
