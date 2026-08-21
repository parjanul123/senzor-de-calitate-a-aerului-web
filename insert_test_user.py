#!/usr/bin/env python
"""Populate users table with current authenticated user"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from config.supabase_client import get_service

supabase = get_service()

print("=" * 100)
print("INSERTING TEST USER INTO SUPABASE USERS TABLE")
print("=" * 100)

# The user ID from the authenticated session
user_id = "3026d270-2ecb-4c61-8724-70573c28be47"
username = "SebiTest"

print(f"\n🔧 Inserting user:")
print(f"   - ID: {user_id}")
print(f"   - Username: {username}")

try:
    result = supabase.create_user(user_id, username)
    
    if result:
        print(f"\n✅ User inserted successfully!")
        print(f"   - Result: {result}")
    else:
        print(f"\n❌ Failed to insert user (result is None)")
        
except Exception as e:
    print(f"\n❌ Error inserting user: {e}")
    import traceback
    traceback.print_exc()

# Verify user was inserted
print("\n🔍 Verifying user...")
try:
    user = supabase.get_user(user_id)
    if user:
        print(f"✅ User verified:")
        print(f"   - ID: {user.get('id')}")
        print(f"   - Username: {user.get('username')}")
    else:
        print(f"❌ User not found")
except Exception as e:
    print(f"❌ Error verifying: {e}")

print("\n" + "=" * 100)
