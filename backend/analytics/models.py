from django.db import models


class UmamiConfig(models.Model):
    """
    Per-site Umami analytics configuration.
    If not configured, analytics will show mock data.
    Note: For production, enable encryption at rest at the database level
    """
    site = models.OneToOneField('sites.Site', on_delete=models.CASCADE, related_name='umami_config')
    api_url = models.URLField(help_text="Umami API endpoint URL")
    api_token = models.CharField(max_length=255, help_text="API token (store encrypted in production)")
    umami_site_id = models.CharField(max_length=100, help_text="Site ID in Umami")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Umami Config for {self.site.domain}"

    class Meta:
        verbose_name = "Umami Configuration"
        verbose_name_plural = "Umami Configurations"


class AnalyticsCache(models.Model):
    """
    Cache for analytics data to reduce API calls.
    Stores aggregated analytics data for specific time periods.
    """
    site = models.ForeignKey('sites.Site', on_delete=models.CASCADE, related_name='analytics_cache')
    date = models.DateField(help_text="Date for this analytics data")
    page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0, help_text="Bounce rate percentage")
    avg_session_duration = models.IntegerField(default=0, help_text="Average session duration in seconds")
    
    # JSON fields for detailed data
    top_pages = models.JSONField(default=list, blank=True, help_text="Top pages with view counts")
    traffic_sources = models.JSONField(default=list, blank=True, help_text="Traffic source breakdown")
    device_breakdown = models.JSONField(default=dict, blank=True, help_text="Device/browser statistics")
    geographic_data = models.JSONField(default=dict, blank=True, help_text="Geographic distribution")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.site.domain} - {self.date}"

    class Meta:
        verbose_name = "Analytics Cache"
        verbose_name_plural = "Analytics Caches"
        unique_together = ['site', 'date']
        ordering = ['-date']
