from rest_framework import serializers
from .models import Site, Page, Block, SwiperPreset, Deployment
from tokens.models import APIToken
from templates.models import Template
from affiliates.models import AffiliateLink
from .serializers_blocks import (
    HeroBlockContentSerializer,
    ArticleBlockContentSerializer,
    ImageBlockContentSerializer,
    TextImageBlockContentSerializer,
    CTABlockContentSerializer,
    FAQBlockContentSerializer,
    SwiperBlockContentSerializer,
    CustomBlockContentSerializer
)

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            'id', 'site', 'title', 'slug', 'description', 
            'meta_title', 'meta_description', 'h1_heading', 'use_h1_in_hero', 'canonical_url', 'custom_head_html',
            'primary_keywords', 'lsi_keywords',
            'published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

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

    def validate_footer_images(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Footer images must be a list.")
        return value

    def validate_header_cta_config(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Header CTA config must be a dictionary.")
        return value

    def validate_microdata_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Microdata settings must be a dictionary.")
        return value

    def create(self, validated_data):
        return validated_data


class SiteListSerializer(serializers.ModelSerializer):
    """Optimized serializer for dashboard site list view."""
    page_count = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    last_deployment_date = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Site
        fields = [
            'id', 'domain', 'brand_name', 'language', 'geo_targeting',
            'created_at', 'updated_at', 'status', 'page_count', 'last_deployment_date'
        ]
        read_only_fields = fields


class SiteDashboardSerializer(serializers.ModelSerializer):
    """Detailed serializer for site-level dashboard."""
    page_count = serializers.IntegerField(read_only=True)
    deployment_count = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    last_deployment_date = serializers.DateTimeField(read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True, allow_null=True)
    affiliate_link_url = serializers.URLField(source='affiliate_link.url', read_only=True, allow_null=True)
    
    class Meta:
        model = Site
        fields = [
            'id', 'name', 'domain', 'owner',
            'language', 'brand_name', 'logo_url', 'favicon_url', 'geo_targeting',
            'template', 'template_name', 'fingerprint_type',
            'affiliate_link', 'affiliate_link_url',
            'allow_indexing', 'redirect_404_to_homepage', 'force_www',
            'page_speed_optimization',
            'microdata_settings', 'header_cta_config', 'footer_images', 
            'custom_head_html', 'custom_body_html', 'custom_css', 'custom_js', 'template_config',
            'created_at', 'updated_at',
            'page_count', 'deployment_count', 'status', 'last_deployment_date'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'page_count', 'deployment_count', 'status', 'last_deployment_date']


class SiteStatisticsSerializer(serializers.Serializer):
    """Serializer for dashboard overview statistics."""
    total_sites = serializers.IntegerField()
    sites_deployed = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    storage_used = serializers.FloatField()  # In MB


class SwiperPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwiperPreset
        fields = ['id', 'site', 'created_by', 'name', 'items', 'button_text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'site': {'required': False, 'allow_null': True}
        }

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'page', 'type', 'order', 'content', 'is_active']
        read_only_fields = ['id']

    def validate(self, data):
        """
        Validate content based on block type using specific serializers.
        """
        block_type = data.get('type')
        content = data.get('content', {})
        
        serializer_map = {
            'hero': HeroBlockContentSerializer,
            'article': ArticleBlockContentSerializer,
            'image': ImageBlockContentSerializer,
            'text_image': TextImageBlockContentSerializer,
            'cta': CTABlockContentSerializer,
            'faq': FAQBlockContentSerializer,
            'faq': FAQBlockContentSerializer,
            'swiper': SwiperBlockContentSerializer,
            'custom': CustomBlockContentSerializer,
        }
        
        if block_type in serializer_map:
            serializer = serializer_map[block_type](data=content)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
        
        return data

class PageContentSerializer(serializers.ModelSerializer):
    blocks = BlockSerializer(many=True, required=False)
    
    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'description', 
            'meta_title', 'meta_description', 'h1_heading', 
            'use_h1_in_hero', 'canonical_url', 'custom_head_html',
            'primary_keywords', 'lsi_keywords', 'published',
            'blocks'
        ]

class DeploymentSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)
    site_domain = serializers.CharField(source='site.domain', read_only=True)
    
    class Meta:
        model = Deployment
        fields = [
            'id', 'site', 'site_name', 'site_domain',
            'status', 'commit_hash', 'log', 
            'created_at', 'finished_at'
        ]
        read_only_fields = ['id', 'created_at', 'finished_at', 'site_name', 'site_domain']
