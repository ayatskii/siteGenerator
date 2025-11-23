from rest_framework import serializers
from .models import APIToken

class APITokenSerializer(serializers.ModelSerializer):
    masked_token = serializers.CharField(read_only=True)
    site_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = APIToken
        fields = [
            'id', 'name', 'service_type', 'token_value', 'ai_model', 
            'is_active', 'last_used_at', 'current_usage', 'created_at', 
            'masked_token', 'site_count'
        ]
        read_only_fields = ['last_used_at', 'current_usage', 'created_at', 'masked_token', 'site_count']
        extra_kwargs = {
            'token_value': {'write_only': True}
        }

    def create(self, validated_data):
        # Set the owner to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
