from django.db import models
from api.models import User

class TextPrompt(models.Model):
    TARGET_TYPE_CHOICES = [
        ('article', 'Article'),
        ('title', 'Title'),
        ('description', 'Description'),
        ('h1', 'H1 Heading'),
        ('faq', 'FAQ'),
        ('hero', 'Hero Section'),
    ]

    AI_MODEL_CHOICES = [
        ('gpt-4', 'GPT-4'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
        ('grok-beta', 'Grok Beta'),
        ('claude-3-opus', 'Claude 3 Opus'),
    ]

    OUTPUT_FORMAT_CHOICES = [
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
        ('text', 'Plain Text'),
    ]

    name = models.CharField(max_length=100, help_text="Human-readable identifier")
    description = models.TextField(blank=True, help_text="Optional description")
    target_type = models.CharField(max_length=50, choices=TARGET_TYPE_CHOICES)
    ai_model = models.CharField(max_length=50, choices=AI_MODEL_CHOICES, default='gpt-4')
    temperature = models.FloatField(default=0.7, help_text="Creativity control (0.0 to 1.0)")
    template = models.TextField(help_text="Prompt text with {{variable}} placeholders")
    input_variables = models.JSONField(default=list, help_text="List of expected variables e.g. ['keywords', 'brand']")
    output_format = models.CharField(max_length=20, choices=OUTPUT_FORMAT_CHOICES, default='html')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='text_prompts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_target_type_display()})"

class ImagePrompt(models.Model):
    PROVIDER_CHOICES = [
        ('openai', 'DALL-E (OpenAI)'),
        ('midjourney', 'Midjourney'),
        ('stability', 'Stability AI'),
    ]

    STYLE_PRESETS = [
        ('realistic', 'Realistic'),
        ('illustrated', 'Illustrated'),
        ('minimalist', 'Minimalist'),
        ('cyberpunk', 'Cyberpunk'),
        ('studio', 'Studio Photo'),
    ]

    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('jpg', 'JPG'),
        ('webp', 'WebP'),
    ]

    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default='openai')
    template = models.TextField(help_text="Image generation prompt")
    style_preset = models.CharField(max_length=50, choices=STYLE_PRESETS, default='realistic')
    width = models.IntegerField(default=1024)
    height = models.IntegerField(default=1024)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='png')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='image_prompts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"