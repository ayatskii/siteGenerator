from rest_framework import serializers 
from .models import User, Token


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "password", "role"]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        name = validated_data.pop('name', '')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        role = validated_data.pop('role', 'USER')
        
        # Split name into first and last name
        parts = name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        return user


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ["token", "created_at", "expires_at", "user_id", "is_used"]