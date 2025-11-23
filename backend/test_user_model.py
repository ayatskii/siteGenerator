import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import User

# Test creating a user
print("Testing User.objects.create_user()...")
try:
    # Check if user exists first
    test_email = "shelltest@example.com"
    if User.objects.filter(email=test_email).exists():
        User.objects.filter(email=test_email).delete()
        print(f"Deleted existing user: {test_email}")
    
    user = User.objects.create_user(
        username=test_email,
        email=test_email,
        password="testpassword123",
        first_name="Test",
        last_name="User"
    )
    print(f"✓ User created successfully: {user.email}")
    print(f"  - ID: {user.id}")
    print(f"  - Username: {user.username}")
    print(f"  - Name: {user.get_full_name()}")
    print(f"  - Role: {user.role}")
    print(f"  - Password (hashed): {user.password[:50]}...")
    
    # Test check_password
    if user.check_password("testpassword123"):
        print("✓ Password check successful")
    else:
        print("✗ Password check failed")
    
    # Clean up
    user.delete()
    print("✓ Test user deleted")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
