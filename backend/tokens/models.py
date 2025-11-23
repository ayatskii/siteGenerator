from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
import requests

User = get_user_model()


class APIToken(models.Model):
    """
    Store API credentials for third-party services
    Note: For production, enable encryption at rest at the database level
    """

    SERVICE_CHOICES = [
        ('openai', 'OpenAI / ChatGPT'),
        ('grok', 'Grok'),
        ('cloudflare', 'Cloudflare Pages'),
        ('openrouter', 'OpenRouter'), 
        ('google', 'Google AI'),
    ]

    AI_MODEL_CHOICES = [
        # OpenAI
        ('gpt-4', 'GPT-4'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        # Grok
        ('grok-beta', 'Grok Beta'),
        # Google
        ('gemini-pro', 'Gemini Pro'),
        ('gemini-ultra', 'Gemini Ultra'),
        # OpenRouter
        ('openrouter/auto', 'OpenRouter Auto'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_tokens',
        help_text='The user who owns this token',
        null=True,
        blank=True
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Friendly name for this token (e.g., "My OpenAI Key")'
    )
    
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        help_text='Which service this token is for'
    )
    
    token_value = models.CharField(
        max_length=500,
        help_text='The actual API token (store encrypted in production)'
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

    def increment_usage(self):
        """
        Increment the usage count for this token.
        """
        self.current_usage += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['current_usage', 'last_used_at'])

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
            response = requests.get(
                'https://api.x.ai/v1/models',
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
                return {
                    'success': True,
                    'message': 'Cloudflare token is valid and working.'
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
        """Test OpenRouter API connection"""
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
                return {
                    'success': True,
                    'message': 'OpenRouter token is valid and working.'
                }
            else:
                return {
                    'success': False,
                    'message': f'OpenRouter API returned status {response.status_code}: {response.text}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'OpenRouter connection error: {str(e)}'
            }
