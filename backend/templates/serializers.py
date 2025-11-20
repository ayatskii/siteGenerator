from rest_framework import serializers
from .models import Template, TemplateSection, TemplateVariable

class TemplateSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateSection
        fields = ['id', 'name', 'content', 'order', 'is_required']

class TemplateSerializer(serializers.ModelSerializer):
    sections = TemplateSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Template
        fields = ['id', 'name', 'type', 'description', 'thumbnail', 'created_at', 'updated_at', 'content', 'config', 'sections']

class TemplateVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateVariable
        fields = ['id', 'name', 'description', 'default_value']
