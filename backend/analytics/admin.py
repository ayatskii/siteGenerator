from django.contrib import admin
from .models import UmamiConfig, AnalyticsCache


@admin.register(UmamiConfig)
class UmamiConfigAdmin(admin.ModelAdmin):
    list_display = ['site', 'api_url', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['site__domain', 'umami_site_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AnalyticsCache)
class AnalyticsCacheAdmin(admin.ModelAdmin):
    list_display = ['site', 'date', 'page_views', 'unique_visitors', 'created_at']
    list_filter = ['date', 'site']
    search_fields = ['site__domain']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
