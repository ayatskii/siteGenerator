from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from fernet_fields import EncryptedCharField
import requests

User = get_user_model()


class APIToken(models.Model):
    """
    Store encrypted API credentials for third-party services
    """

    SERVICE_CHOICES = [
        ('openai', 'OpenAI / ChatGPT'),
        ('grok', 'Grok'),
        ('cloudflare', 'Cloudflare Pages'),
        ('openrouter', 'OpenRouter'), 
    ]
    
    AI_MODEL_CHOICES = [
        # OpenAI models
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        # Grok models
        ('grok-beta', 'Grok Beta'),
        # OpenRouter models (examples - supports 400+ models)
        ('openai/gpt-4', 'OpenRouter: GPT-4'),
        ('openai/gpt-4-turbo', 'OpenRouter: GPT-4 Turbo'),
        ('openai/gpt-3.5-turbo', 'OpenRouter: GPT-3.5 Turbo'),
        ('anthropic/claude-3.5-sonnet', 'OpenRouter: Claude 3.5 Sonnet'),
        ('anthropic/claude-3-opus', 'OpenRouter: Claude 3 Opus'),
        ('anthropic/claude-3-haiku', 'OpenRouter: Claude 3 Haiku'),
        ('google/gemini-2.0-flash-exp', 'OpenRouter: Gemini 2.0 Flash'),
        ('google/gemini-pro-1.5', 'OpenRouter: Gemini Pro 1.5'),
        ('meta-llama/llama-3.1-70b-instruct', 'OpenRouter: Llama 3.1 70B'),
        ('mistralai/mistral-large', 'OpenRouter: Mistral Large'),
        ('x-ai/grok-2', 'OpenRouter: Grok 2'),
        ('deepseek/deepseek-chat', 'OpenRouter: DeepSeek Chat'),
        ('qwen/qwen-2.5-72b-instruct', 'OpenRouter: Qwen 2.5 72B'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text='Human-readable identifier for the token (e.g., "Production OpenAI", "OpenRouter Multi-Model")'
    )
    
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        help_text='Which service this token is for'
    )
    
    token_value = EncryptedCharField(
        max_length=500,
        help_text='The actual API token (encrypted in database)'
    )
    
    ai_model = models.CharField(
        max_length=100,
        choices=AI_MODEL_CHOICES,
        null=True,
        blank=True,
        help_text='AI model to use (only for OpenAI/Grok/OpenRouter tokens)'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Whether this token is available for use'
    )
        
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this token was last used for an API call'
    )
    
    current_usage = models.IntegerField(default=0, help_text='Total usage count for this token')

    created_by = models.ForeignKey(
        'api.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tokens',
        help_text='Admin user who created this token'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['service_type', 'name']
        verbose_name = "API Token"
        verbose_name_plural = "API Tokens"
        indexes = [
            models.Index(fields=['service_type', 'is_active'], name='apitoken_service_active_idx'),
            models.Index(fields=['service_type'], name='apitoken_service_idx'),
            models.Index(fields=['is_active'], name='apitoken_active_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"
    
    def clean(self):
        """
        Custom validation
        """
        super().clean()
        
        if self.service_type in ['openai', 'grok', 'openrouter']:
            if not self.ai_model:
                raise ValidationError({
                    'ai_model': f'AI model selection is required for {self.get_service_type_display()} tokens.'
                })

        if self.service_type == 'cloudflare':
            self.ai_model = None

    def save(self, *args, **kwargs):
        """
        Override save to run validation
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def get_masked_token(self):
        """
        Return token with only last 4 characters visible
        Returns: String like "****abcd"
        """
        if not self.token_value:
            return "****"
        
        token_str = str(self.token_value)
        if len(token_str) <= 4:
            return "****"
        
        return "*" * (len(token_str) - 4) + token_str[-4:]
    
    def test_connection(self):
        """
        Make test API call to verify token is valid
        Returns: dict with 'success' (bool) and 'message' (str)
        """
        try:
            if self.service_type == 'openai':
                return self._test_openai_connection()
            elif self.service_type == 'grok':
                return self._test_grok_connection()
            elif self.service_type == 'cloudflare':
                return self._test_cloudflare_connection()
            elif self.service_type == 'openrouter':
                return self._test_openrouter_connection()
            else:
                return {
                    'success': False,
                    'message': f'Unknown service type: {self.service_type}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }
    
    def _test_openai_connection(self):
        """Test OpenAI API connection"""
        headers = {
            'Authorization': f'Bearer {self.token_value}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'OpenAI token is valid and working.'
                }
            else:
                return {
                    'success': False,
                    'message': f'OpenAI API returned status {response.status_code}: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'OpenAI connection error: {str(e)}'
            }
    
    def _test_grok_connection(self):
        """Test Grok API connection"""
        headers = {
            'Authorization': f'Bearer {self.token_value}',
            'Content-Type': 'application/json'
        }
        try:
            # TODO Replace with actual Grok API endpoint
            response = requests.get(
                'https://api.x.ai/v1/models',  # Example endpoint
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Grok token is valid and working.'
                }
            else:
                return {
                    'success': False,
                    'message': f'Grok API returned status {response.status_code}: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Grok connection error: {str(e)}'
            }
    
    def _test_cloudflare_connection(self):
        """Test Cloudflare API connection"""
        headers = {
            'Authorization': f'Bearer {self.token_value}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(
                'https://api.cloudflare.com/client/v4/user/tokens/verify',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'message': 'Cloudflare token is valid and working.'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Cloudflare token verification failed: {data.get("errors", [])}'
                    }
            else:
                return {
                    'success': False,
                    'message': f'Cloudflare API returned status {response.status_code}: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Cloudflare connection error: {str(e)}'
            }
    
    def _test_openrouter_connection(self):
        """
        Test OpenRouter API connection
        OpenRouter uses OpenAI-compatible endpoints
        """
        headers = {
            'Authorization': f'Bearer {self.token_value}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://yourapp.com',  # Optional but recommended TODO
            'X-Title': 'Your App Name',  # Optional but recommended TODO
        }
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json={
                    'model': self.ai_model or 'openai/gpt-3.5-turbo',
                    'messages': [
                        {
                            'role': 'user',
                            'content': 'Hello'
                        }
                    ],
                    'max_tokens': 5
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                model_used = data.get('model', 'unknown')
                return {
                    'success': True,
                    'message': f'OpenRouter token is valid. Test completed with model: {model_used}'
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': 'OpenRouter token is invalid or expired. Please check your API key.'
                }
            elif response.status_code == 402:
                return {
                    'success': False,
                    'message': 'OpenRouter account has insufficient credits. Please add credits to your account.'
                }
            elif response.status_code == 429:
                return {
                    'success': False,
                    'message': 'OpenRouter rate limit exceeded. Please try again later.'
                }
            else:
                return {
                    'success': False,
                    'message': f'OpenRouter API returned status {response.status_code}: {response.text}'
                }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'OpenRouter connection timed out. Please try again.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'OpenRouter connection error: {str(e)}'
            }
    
    def make_openrouter_request(self, messages, temperature=0.7, max_tokens=1000, **kwargs):
        """
        Make a chat completion request to OpenRouter
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Float between 0 and 1
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (top_p, frequency_penalty, etc.)
        
        Returns:
            dict: Response from OpenRouter API
        """
        if self.service_type != 'openrouter':
            raise ValueError('This method only works with OpenRouter tokens')
        
        headers = {
            'Authorization': f'Bearer {self.token_value}',
            'Content-Type': 'application/json',
            'HTTP-Referer': kwargs.pop('referer', 'https://yourapp.com'),
            'X-Title': kwargs.pop('app_title', 'Site Generator Panel'),
        }
        
        payload = {
            'model': self.ai_model or 'openai/gpt-3.5-turbo',
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            self.increment_usage()
            
            return {
                'success': True,
                'data': response.json()
            }
            
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': f'HTTP error: {e.response.status_code}',
                'message': e.response.text
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': 'Request failed',
                'message': str(e)
            }
    
    def get_available_openrouter_models(self):
        """
        Fetch list of available models from OpenRouter
        Returns: dict with 'success' and 'models' list
        """
        if self.service_type != 'openrouter':
            return {
                'success': False,
                'message': 'This method only works with OpenRouter tokens'
            }
        
        headers = {
            'Authorization': f'Bearer {self.token_value}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'models': data.get('data', [])
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to fetch models: {response.status_code}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Error fetching models: {str(e)}'
            }
    
    def get_site_count(self):
        """
        For Cloudflare tokens, count how many sites use this token
        Returns: int (number of sites)
        """
        if self.service_type != 'cloudflare':
            return 0
        if hasattr(self, 'sites'):
            return self.sites.filter(is_active=True).count()
        return 0
    
    @property
    def site_count(self):
        """
        Property for site count (for Cloudflare tokens only)
        Returns: int
        """
        return self.get_site_count()
    
    @property
    def masked_token(self):
        """
        Property accessor for masked token
        Returns: String like "****abcd"
        """
        return self.get_masked_token()
