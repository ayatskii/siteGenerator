from rest_framework import serializers
from .models import UmamiConfig, AnalyticsCache


class UmamiConfigSerializer(serializers.ModelSerializer):
    """Serializer for Umami configuration."""
    
    class Meta:
        model = UmamiConfig
        fields = ['id', 'site', 'api_url', 'umami_site_id', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_token': {'write_only': True}
        }


class AnalyticsDataSerializer(serializers.Serializer):
    """Serializer for analytics data response."""
    page_views_timeline = serializers.ListField(child=serializers.DictField())
    visitors_summary = serializers.DictField()
    top_pages = serializers.ListField(child=serializers.DictField())
    traffic_sources = serializers.ListField(child=serializers.DictField())
    device_breakdown = serializers.DictField()
    geographic_data = serializers.ListField(child=serializers.DictField())
    bounce_rate = serializers.FloatField()
    avg_session_duration = serializers.IntegerField()


class AnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for analytics summary."""
    total_page_views = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()
    bounce_rate = serializers.FloatField()
    avg_session_duration = serializers.IntegerField()
    change_from_previous = serializers.DictField()
    period = serializers.DictField()


class TopPagesSerializer(serializers.Serializer):
    """Serializer for top pages data."""
    path = serializers.CharField()
    title = serializers.CharField()
    views = serializers.IntegerField()
    unique_visitors = serializers.IntegerField()


class TrafficSourceSerializer(serializers.Serializer):
    """Serializer for traffic sources."""
    name = serializers.CharField()
    percentage = serializers.IntegerField()
    visitors = serializers.IntegerField()
    color = serializers.CharField()
