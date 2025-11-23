from rest_framework import serializers
from .models import AffiliateLink

class AffiliateLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateLink
        fields = ['id', 'name', 'url', 'link_type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
