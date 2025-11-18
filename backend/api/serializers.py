from rest_framework import serializers 
from .models import User, Token


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "password", "role"]
        extra_kwargs = {
            'password': {'write_only': True}
        }


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ["token", "created_at", "expires_at", "user_id", "is_used"]