import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from sites.serializers import SiteCreateSerializer
from tokens.models import APIToken
from django.contrib.auth import get_user_model

User = get_user_model()

def test_site_create_serializer():
    # Setup
    user = User.objects.create(username='testuser', email='test@example.com')
    token = APIToken.objects.create(name='Test Token', service_type='cloudflare', token='123', user=user)
    
    data = {
        'domain': 'example.com',
        'cloudflare_token_id': token.id,
        'brand_name': 'Test Brand',
        'footer_images': ['http://example.com/image.png'],
        'header_cta_config': {'enabled': True, 'button1': {'text': 'Click Me'}},
        'microdata_settings': {'inherit_presets': True},
        'custom_head_html': '<meta name="test" content="test">'
    }
    
    serializer = SiteCreateSerializer(data=data)
    if serializer.is_valid():
        print("Serializer validation passed!")
        print(serializer.validated_data)
    else:
        print("Serializer validation failed!")
        print(serializer.errors)

    # Test invalid data
    invalid_data = data.copy()
    invalid_data['footer_images'] = "not a list"
    serializer = SiteCreateSerializer(data=invalid_data)
    if not serializer.is_valid():
        print("Invalid footer_images correctly rejected.")
    else:
        print("Error: Invalid footer_images accepted.")

if __name__ == "__main__":
    try:
        test_site_create_serializer()
    except Exception as e:
        print(f"An error occurred: {e}")
