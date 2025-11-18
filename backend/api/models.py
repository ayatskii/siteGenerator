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

    def __str__(self):
        return self.name
    
    