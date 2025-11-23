from django.db import models
from api.models import User

class AffiliateLink(models.Model):
    LINK_TYPE_CHOICES = [
        ('static', 'Static'),
        ('dynamic', 'Dynamic'),
    ]
    name = models.CharField(max_length=200, help_text="Human-readable name for the link")
    url = models.URLField(help_text="The actual affiliate URL or template")
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='static')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='affiliate_links')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
