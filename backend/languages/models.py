from django.db import models
from django.core.exceptions import ValidationError
import re

class LanguagePreset(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    ordering = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = "Language Preset"
        verbose_name_plural = "Language Presets"
        indexes = [
            models.Index(fields=['code'], name='language_code_idx'),
        ]
    
    def clean(self):
        """
        Custom validation method called by full_clean()
        """
        super().clean()
        
        if self.code:
            pattern = r'^[a-z]{2}-[A-Z]{2}$'
            if not re.match(pattern, self.code):
                raise ValidationError({
                    'code': 'Language code must be in format: language-COUNTRY (e.g., en-US, fr-FR)'
                })
        
        if not self.name or not self.name.strip():
            raise ValidationError({
                'name': 'Language name cannot be empty.'
            })
        
        if self.code:
            duplicate = LanguagePreset.objects.filter(
                code__iexact=self.code
            ).exclude(pk=self.pk).exists()
            
            if duplicate:
                raise ValidationError({
                    'code': f'Language code "{self.code}" already exists.'
                })
    
    def __str__(self):
        return f"{self.name} ({self.code})"
