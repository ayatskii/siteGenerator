from django.db import models
from api.models import User

class AffiliateLink(models.Model):
    name = models.CharField(max_length=200, help_text="Human-readable name for the link")
    url = models.URLField(help_text="The actual affiliate URL")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='affiliate_links')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
