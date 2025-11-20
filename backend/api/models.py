from django.db import models

class Token(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    user_id = models.IntegerField()
    is_used = models.BooleanField()

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=[("USER", "user"), ("ADMIN", "admin")], default="USER")
    default_media_folder = models.ForeignKey('media_library.MediaFolder', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_for_users')
    preferences = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return self.name