import requests
import json

# First, register a test user
register_url = "http://127.0.0.1:8000/api/register/"
login_url = "http://127.0.0.1:8000/api/login/"

test_email = f"logintest{__import__('random').randint(1000,9999)}@example.com"
test_password = "securepassword123"

print("=== Testing Registration and Login ===\n")

# Register
print(f"1. Registering user: {test_email}")
register_data = {
    "name": "Login Test User",
    "email": test_email,
    "password": test_password
}

try:
    response = requests.post(register_url, json=register_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print(f"   ✓ Registration successful!")
    else:
        print(f"   Response: {response.json()}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Login
print(f"\n2. Logging in with: {test_email}")
login_data = {
    "email": test_email,
    "password": test_password
}

try:
    response = requests.post(login_url, json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Login successful!")
        print(f"   User: {data['user']['name']}")
        print(f"   Email: {data['user']['email']}")
        print(f"   Role: {data['user']['role']}")
        print(f"   Access Token: {data['access'][:50]}...")
    else:
        print(f"   Response: {response.json()}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n=== Test Complete ===")
