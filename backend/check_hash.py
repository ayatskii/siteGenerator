from django.contrib.auth.hashers import make_password

SALT = "8b4f6b2cc1868d75ef79e5cfb8779c11b6a374bf0fce05b485581bf4e1e25b96c8c2855015de8449"
hashed = make_password("password123", salt=SALT)
print(f"Length: {len(hashed)}")
print(f"Hash: {hashed}")
