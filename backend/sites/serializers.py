from rest_framework import serializers
from .models import Site, Page, Block, SwiperPreset
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
    SwiperBlockContentSerializer
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

    def create(self, validated_data):
        # This method might not be used directly if we handle logic in ViewSet, 
        # but good to have for standard usage.
        # However, we have complex logic (Cloudflare API, Page creation), so ViewSet might be better place 
        # or we override create here.
        # Let's keep it simple here and handle orchestration in ViewSet or Service.
        return validated_data

class SwiperPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwiperPreset
        fields = ['id', 'site', 'name', 'items', 'button_text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

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
            'swiper': SwiperBlockContentSerializer,
        }
        
        if block_type in serializer_map:
            serializer = serializer_map[block_type](data=content)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)
            # Optionally replace content with validated data to strip unknown fields
            # data['content'] = serializer.validated_data 
        
        return data
