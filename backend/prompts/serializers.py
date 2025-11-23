from rest_framework import serializers
from .models import TextPrompt, ImagePrompt

class TextPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextPrompt
        fields = ['id', 'name', 'description', 'target_type', 'ai_model', 'temperature', 'template', 'input_variables', 'output_format', 'is_active', 'created_at', 'updated_at']

class ImagePromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagePrompt
        fields = ['id', 'name', 'provider', 'template', 'style_preset', 'width', 'height', 'format', 'created_at', 'updated_at']

class GenerationItemSerializer(serializers.Serializer):
    block_id = serializers.IntegerField(required=True)
    prompt_id = serializers.IntegerField(required=True)
    target_field = serializers.CharField(required=False, default='body')
    extra_context = serializers.DictField(required=False, default=dict)

class BulkGenerationRequestSerializer(serializers.Serializer):
    page_id = serializers.IntegerField(required=True)
    generations = GenerationItemSerializer(many=True)

class GenerationResponseSerializer(serializers.Serializer):
    block_id = serializers.IntegerField()
    content = serializers.CharField(required=False, allow_blank=True)
    success = serializers.BooleanField()
    error = serializers.CharField(required=False, allow_blank=True)

class BulkGenerationResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    results = GenerationResponseSerializer(many=True)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
