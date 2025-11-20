import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import User
from affiliates.models import AffiliateLink
from media_library.models import MediaFolder, MediaAsset
from tokens.models import APIToken
from languages.models import LanguagePreset
from prompts.models import TextPrompt, ImagePrompt

def verify():
    print("Verifying models...")

    # Cleanup previous test data
    User.objects.filter(name="TestUser").delete()
    print("Cleaned up previous test data.")

    # Create User
    user, created = User.objects.get_or_create(name="TestUser", email="test@example.com", password="password")
    print(f"User: {user}")

    # Create Affiliate Link
    link, created = AffiliateLink.objects.get_or_create(name="Test Link", defaults={'url': "https://example.com", 'created_by': user})
    print(f"Affiliate Link: {link}")

    # Create Media Folder
    folder, created = MediaFolder.objects.get_or_create(name="Test Folder", owner=user)
    print(f"Media Folder: {folder}")

    # Create Media Asset
    asset, created = MediaAsset.objects.get_or_create(
        filename="test.jpg", 
        folder=folder, 
        owner=user, 
        defaults={'size': 100}
    )
    print(f"Media Asset: {asset}")

    # Create Language Preset
    lang, created = LanguagePreset.objects.get_or_create(
        code="es-ES", 
        defaults={'name': "Spanish", 'ordering': 1}
    )
    print(f"Language Preset: {lang}")

    # Create API Token
    token, created = APIToken.objects.get_or_create(
        name="Test Token", 
        defaults={
            'service_type': "openai", 
            'token_value': "sk-test", 
            'ai_model': "gpt-4",
            'created_by': user
        }
    )
    print(f"API Token: {token}")
    
    # Verify User extensions
    user.default_media_folder = folder
    user.preferences = {"theme": "dark"}
    user.save()
    print(f"User Preferences: {user.preferences}")
    print(f"User Default Folder: {user.default_media_folder}")

    # Create Text Prompt
    text_prompt, created = TextPrompt.objects.get_or_create(
        name="Article Generator",
        defaults={
            'target_type': "article",
            'template': "Write an article about {{keywords}}",
            'input_variables': ["keywords"],
            'created_by': user
        }
    )
    print(f"Text Prompt: {text_prompt}")

    # Create Image Prompt
    image_prompt, created = ImagePrompt.objects.get_or_create(
        name="Hero Image",
        defaults={
            'provider': "openai",
            'template': "A futuristic city",
            'created_by': user
        }
    )
    print(f"Image Prompt: {image_prompt}")

    print("Verification successful!")

if __name__ == "__main__":
    verify()
