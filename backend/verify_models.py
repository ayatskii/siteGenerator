import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import User
from affiliates.models import AffiliateLink
from media_library.models import MediaFolder, MediaAsset
from tokens.models import APIToken
from languages.models import LanguagePreset

def verify():
    print("Verifying models...")

    # Create User
    user, created = User.objects.get_or_create(name="TestUser", email="test@example.com", password="password")
    print(f"User: {user}")

    # Create Affiliate Link
    link = AffiliateLink.objects.create(name="Test Link", url="https://example.com", created_by=user)
    print(f"Affiliate Link: {link}")

    # Create Media Folder
    folder = MediaFolder.objects.create(name="Test Folder", owner=user)
    print(f"Media Folder: {folder}")

    # Create Media Asset
    # We won't upload a real file, just check model creation
    asset = MediaAsset(filename="test.jpg", folder=folder, owner=user, size=100)
    asset.save()
    print(f"Media Asset: {asset}")

    # Create Language Preset
    lang = LanguagePreset.objects.create(code="es-ES", name="Spanish", ordering=1)
    print(f"Language Preset: {lang}")

    # Create API Token
    token = APIToken.objects.create(
        name="Test Token", 
        service_type="openai", 
        token_value="sk-test", 
        ai_model="gpt-4",
        created_by=user
    )
    print(f"API Token: {token}")
    
    # Verify User extensions
    user.default_media_folder = folder
    user.preferences = {"theme": "dark"}
    user.save()
    print(f"User Preferences: {user.preferences}")
    print(f"User Default Folder: {user.default_media_folder}")

    # Create Text Prompt
    from prompts.models import TextPrompt, ImagePrompt
    
    text_prompt = TextPrompt.objects.create(
        name="Article Generator",
        target_type="article",
        template="Write an article about {{keywords}}",
        input_variables=["keywords"],
        created_by=user
    )
    print(f"Text Prompt: {text_prompt}")

    # Create Image Prompt
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import User
from affiliates.models import AffiliateLink
from media_library.models import MediaFolder, MediaAsset
from tokens.models import APIToken
from languages.models import LanguagePreset

def verify():
    print("Verifying models...")

    # Create User
    user, created = User.objects.get_or_create(name="TestUser", email="test@example.com", password="password")
    print(f"User: {user}")

    # Create Affiliate Link
    link = AffiliateLink.objects.create(name="Test Link", url="https://example.com", created_by=user)
    print(f"Affiliate Link: {link}")

    # Create Media Folder
    folder = MediaFolder.objects.create(name="Test Folder", owner=user)
    print(f"Media Folder: {folder}")

    # Create Media Asset
    # We won't upload a real file, just check model creation
    asset = MediaAsset(filename="test.jpg", folder=folder, owner=user, size=100)
    asset.save()
    print(f"Media Asset: {asset}")

    # Create Language Preset
    lang = LanguagePreset.objects.create(code="es-ES", name="Spanish", ordering=1)
    print(f"Language Preset: {lang}")

    # Create API Token
    token = APIToken.objects.create(
        name="Test Token", 
        service_type="openai", 
        token_value="sk-test", 
        ai_model="gpt-4",
        created_by=user
    )
    print(f"API Token: {token}")
    
    # Verify User extensions
    user.default_media_folder = folder
    user.preferences = {"theme": "dark"}
    user.save()
    print(f"User Preferences: {user.preferences}")
    print(f"User Default Folder: {user.default_media_folder}")

    # Create Text Prompt
    from prompts.models import TextPrompt, ImagePrompt
    
    text_prompt = TextPrompt.objects.create(
        name="Article Generator",
        target_type="article",
        template="Write an article about {{keywords}}",
        input_variables=["keywords"],
        created_by=user
    )
    print(f"Text Prompt: {text_prompt}")

    # Create Image Prompt
    image_prompt = ImagePrompt.objects.create(
        name="Hero Image",
        provider="openai",
        template="A futuristic city",
        created_by=user
    )
    print(f"Image Prompt: {image_prompt}")

    print("Verification successful!")

if __name__ == "__main__":
    verify()
