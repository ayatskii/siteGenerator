from rest_framework import serializers

class HeroBlockContentSerializer(serializers.Serializer):
    headline = serializers.CharField(required=False, allow_blank=True)
    subheading = serializers.CharField(required=False, allow_blank=True)
    image_id = serializers.IntegerField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    cta_buttons = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    
    def validate(self, data):
        if not data.get('headline') and not data.get('image_id') and not data.get('image_url'):
            # It's okay to be empty initially, but maybe warn? 
            # For now, allow empty as per "Empty/Not filled" state requirement.
            pass
        return data

class ArticleBlockContentSerializer(serializers.Serializer):
    html_content = serializers.CharField(required=False, allow_blank=True)
    markdown_content = serializers.CharField(required=False, allow_blank=True)
    use_article_tag = serializers.BooleanField(default=False)
    
    def validate(self, data):
        if not data.get('html_content') and not data.get('markdown_content'):
            # Allow empty for initial state
            pass
        return data

class ImageBlockContentSerializer(serializers.Serializer):
    image_id = serializers.IntegerField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    alt_text = serializers.CharField(required=False, allow_blank=True)
    title_attribute = serializers.CharField(required=False, allow_blank=True)
    width = serializers.CharField(required=False, allow_blank=True)
    height = serializers.CharField(required=False, allow_blank=True)

class TextImageBlockContentSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True)
    image_id = serializers.IntegerField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    position = serializers.ChoiceField(choices=['left', 'right'], default='left')
    alt_text = serializers.CharField(required=False, allow_blank=True)

class CTABlockContentSerializer(serializers.Serializer):
    buttons = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    layout = serializers.ChoiceField(choices=['horizontal', 'vertical'], default='horizontal')

class FAQBlockContentSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    title = serializers.CharField(required=False, allow_blank=True)

class SwiperBlockContentSerializer(serializers.Serializer):
    preset_id = serializers.IntegerField(required=False, allow_null=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    auto_scroll = serializers.BooleanField(default=False)
    interval = serializers.IntegerField(default=3000)
    
class CustomBlockContentSerializer(serializers.Serializer):
    html = serializers.CharField(required=False, allow_blank=True)
    css = serializers.CharField(required=False, allow_blank=True)
    js = serializers.CharField(required=False, allow_blank=True)
