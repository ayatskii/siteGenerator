from rest_framework import serializers
from .models import Site, Page
from tokens.models import APIToken
from templates.models import Template
from affiliates.models import AffiliateLink

class SiteCreateSerializer(serializers.ModelSerializer):
    cloudflare_token_id = serializers.IntegerField(write_only=True)
    template_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    affiliate_link_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Site
        fields = [
            'name', 'domain', 'cloudflare_token_id', 
            'language', 'brand_name', 'logo_url', 'favicon_url', 'geo_targeting',
            'template_id', 'fingerprint_type',
            'affiliate_link_id',
            'allow_indexing', 'redirect_404_to_homepage', 'force_www',
            'page_speed_optimization',
            'microdata_settings', 'header_cta_config', 'footer_images', 'custom_head_html',
            'pages_structure' # Virtual field for page structure
        ]
        extra_kwargs = {
            'name': {'required': False} # Can be derived from brand or domain
        }

    pages_structure = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        default=list
    )

    def validate_cloudflare_token_id(self, value):
        try:
            token = APIToken.objects.get(id=value, service_type='cloudflare')
            return value
        except APIToken.DoesNotExist:
            raise serializers.ValidationError("Invalid Cloudflare token.")

    def create(self, validated_data):
        # This method might not be used directly if we handle logic in ViewSet, 
        # but good to have for standard usage.
        # However, we have complex logic (Cloudflare API, Page creation), so ViewSet might be better place 
        # or we override create here.
        # Let's keep it simple here and handle orchestration in ViewSet or Service.
        return validated_data
