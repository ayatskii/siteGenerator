from rest_framework import serializers
from .models import LanguagePreset

class LanguagePresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguagePreset
        fields = ['id', 'code', 'name', 'ordering', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
