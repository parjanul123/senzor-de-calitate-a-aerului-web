#!/usr/bin/env python
"""Check users table data"""

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
print("CHECKING USERS TABLE DATA")
print("=" * 100)

try:
    # Get all users
    response = supabase.client.table('users').select('*').execute()
    users = response.data if response.data else []
    
    print(f"\n✅ Total users: {len(users)}")
    
    if users:
        # Show first user
        print("\n📋 First User Structure:")
        first_user = users[0]
        for key, value in first_user.items():
            print(f"   - {key}: {value}")
        
        # Show all users
        print("\n📊 All Users:")
        for i, user in enumerate(users, 1):
            print(f"\n   User #{i}:")
            print(f"      ID: {user.get('id')}")
            print(f"      Username: {user.get('username')}")
            print(f"      Email: {user.get('email')}")
            print(f"      Created: {user.get('created_at')}")
    else:
        print("\n❌ No users found in database!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Also check the current session user
print("\n" + "=" * 100)
print("CURRENT SESSION USER")
print("=" * 100)

from django.http import HttpRequest
from django.contrib.sessions.backends.db import SessionStore

# Try to get from request context if available
try:
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get('/')
    request.session = SessionStore()
    print(f"\nNote: To get current user, you need to be in a request context")
except:
    print("\nNote: Session inspection requires request context")

print("\n" + "=" * 100)
