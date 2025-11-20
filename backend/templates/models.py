from django.db import models

class Template(models.Model):
    TYPE_CHOICES = (
        ('MONOLITHIC', 'Monolithic'),
        ('SECTIONAL', 'Sectional'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='template_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For Monolithic templates: full HTML content
    content = models.TextField(blank=True, help_text="Full HTML content for Monolithic templates")
    
    # Configuration for both types (variables list, etc.)
    config = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

class TemplateSection(models.Model):
    template = models.ForeignKey(Template, related_name='sections', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, help_text="e.g., Header, Footer, Sidebar")
    content = models.TextField(help_text="HTML content of the section")
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.template.name} - {self.name}"

class TemplateVariable(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="e.g., SITE_BRAND")
    description = models.TextField(blank=True)
    default_value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
