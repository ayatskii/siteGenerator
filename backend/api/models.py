from django.db import models
from django.contrib.auth.models import AbstractUser

class Token(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    user_id = models.IntegerField()
    is_used = models.BooleanField()

class User(AbstractUser):
    # AbstractUser already provides: username, first_name, last_name, email, password, groups, user_permissions, is_staff, is_active, date_joined
    
    # Explicitly define username to allow nullable for migration
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    
    role = models.CharField(max_length=20, choices=[("USER", "user"), ("ADMIN", "admin")], default="USER")
    default_media_folder = models.ForeignKey('media_library.MediaFolder', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_for_users')
    preferences = models.JSONField(default=dict, blank=True)
    
    # Fix for unique email requirement
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username if self.username else self.email