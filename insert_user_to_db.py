#!/usr/bin/env python
"""Insert current user into users table"""

import os
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from config.supabase_client import get_service

supabase = get_service()

# The current authenticated user's ID from our context
CURRENT_USER_ID = "3026d270-2ecb-4c61-8724-70573c28be47"  # From previous session

print("=" * 100)
print("INSERTING USER INTO DATABASE")
print("=" * 100)

try:
    # Generate a username based on UUID
    username = f"Utilizator_{CURRENT_USER_ID[:8]}"
    
    # Check if user already exists
    check_response = supabase.client.table('users').select('*').eq('id', CURRENT_USER_ID).execute()
    
    if check_response.data and len(check_response.data) > 0:
        print(f"\n⚠️  User already exists: {CURRENT_USER_ID}")
        existing_user = check_response.data[0]
        print(f"   Username: {existing_user.get('username')}")
        print(f"   Created: {existing_user.get('created_at')}")
    else:
        # Insert new user
        user_data = {
            'id': CURRENT_USER_ID,
            'username': username,
            'email': None,  # We don't have email from QR login
            'created_at': 'now()',  # Supabase will set this
        }
        
        response = supabase.client.table('users').insert(user_data).execute()
        
        if response.data:
            print(f"\n✅ User inserted successfully!")
            print(f"   ID: {CURRENT_USER_ID}")
            print(f"   Username: {username}")
            print(f"   Created: {response.data[0].get('created_at')}")
        else:
            print(f"\n❌ Failed to insert user")
            
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Verify data was inserted
print("\n" + "=" * 100)
print("VERIFICATION")
print("=" * 100)

try:
    response = supabase.client.table('users').select('*').eq('id', CURRENT_USER_ID).execute()
    
    if response.data:
        print(f"\n✅ User found in database:")
        user = response.data[0]
        for key, value in user.items():
            print(f"   - {key}: {value}")
    else:
        print(f"\n❌ User not found")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 100)
