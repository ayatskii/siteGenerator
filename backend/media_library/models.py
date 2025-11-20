from django.db import models
from api.models import User
import os

class MediaFolder(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_folders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'parent', 'owner']
        ordering = ['name']

    def __str__(self):
        return self.name

class MediaAsset(models.Model):
    file = models.ImageField(upload_to='media_library/%Y/%m/')
    filename = models.CharField(max_length=255)
    folder = models.ForeignKey(MediaFolder, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_assets')
    alt_text = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(help_text="File size in bytes")
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.filename and self.file:
            self.filename = os.path.basename(self.file.name)
        if not self.size and self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return self.filename

    class Meta:
        ordering = ['-created_at']
