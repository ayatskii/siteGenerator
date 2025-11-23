import requests
import json

url_register = "http://127.0.0.1:8000/api/register"

data = {
    "name": "John Doe",
    "email": f"testuser{__import__('random').randint(1000,9999)}@example.com",
    "password": "securepassword123"
}

print(f"Attempting to register user: {data['email']}")

try:
    response = requests.post(url_register, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"\nRaw Response (first 500 chars):")
    print(response.text[:500])
    
    if response.headers.get('Content-Type', '').startswith('application/json'):
        print(f"\nJSON Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
