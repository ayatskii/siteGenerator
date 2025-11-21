from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Site(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sites')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Configuration
    language = models.CharField(max_length=10, default='en-US')
    brand_name = models.CharField(max_length=255, blank=True)
    logo_url = models.URLField(blank=True)
    favicon_url = models.URLField(blank=True)
    geo_targeting = models.CharField(max_length=100, blank=True, help_text="Optional region for optimization")
    
    # Template & Fingerprinting
    template = models.ForeignKey('templates.Template', on_delete=models.SET_NULL, null=True, blank=True)
    fingerprint_type = models.CharField(max_length=50, default='random_class', choices=[
        ('random_class', 'Random Class Names'),
        ('preset_scheme', 'Preset Naming Scheme'),
        ('wordpress', 'WordPress Footprint'),
        ('other_cms', 'Other CMS Footprint'),
    ])
    
    # Affiliate
    affiliate_link = models.ForeignKey('affiliates.AffiliateLink', on_delete=models.SET_NULL, null=True, blank=True)
    
    # SEO & Cloudflare
    allow_indexing = models.BooleanField(default=True, help_text="If false, adds noindex meta tag")
    redirect_404_to_homepage = models.BooleanField(default=False)
    force_www = models.BooleanField(default=False)
    
    # Optimization
    page_speed_optimization = models.BooleanField(default=False, help_text="Enable image optimization and lazy loading")
    
    # Advanced Config
    microdata_settings = models.JSONField(default=dict, blank=True)
    header_cta_config = models.JSONField(default=dict, blank=True)
    footer_images = models.JSONField(default=list, blank=True)
    custom_head_html = models.TextField(blank=True, help_text="Custom HTML for <head> section")
    
    def __str__(self):
        return self.name

class Page(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='pages')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    h1 = models.CharField(max_length=255, blank=True)
    canonical_url = models.URLField(blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['site', 'slug']

    def __str__(self):
        return f"{self.site.name} - {self.title}"

class Block(models.Model):
    BLOCK_TYPES = [
        ('hero', 'Hero Section'),
        ('article', 'Article'),
        ('image', 'Image'),
        ('cta', 'Call to Action'),
        ('faq', 'FAQ'),
        ('swiper', 'Swiper/Slider'),
        ('custom', 'Custom HTML'),
    ]

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='blocks')
    type = models.CharField(max_length=50, choices=BLOCK_TYPES)
    order = models.IntegerField(default=0)
    content = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.page.title} - {self.get_type_display()}"

class Deployment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='deployments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    commit_hash = models.CharField(max_length=100, blank=True)
    log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.site.name} - {self.created_at} ({self.status})"
