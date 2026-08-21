#!/usr/bin/env python
"""Check users table structure in Supabase"""

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
print("CHECKING SUPABASE USERS TABLE")
print("=" * 100)

try:
    # Fetch first user to see structure
    response = supabase.client.table('users').select('*').limit(1).execute()
    
    if response.data:
        user = response.data[0]
        print(f"\n✅ Found user:")
        for key, value in user.items():
            print(f"   - {key}: {value}")
    else:
        print("\n❌ No users found, fetching all rows...")
        response = supabase.client.table('users').select('*').execute()
        print(f"Total users: {len(response.data) if response.data else 0}")
        
        if response.data:
            for i, user in enumerate(response.data[:3], 1):
                print(f"\n📍 User {i}:")
                for key, value in user.items():
                    print(f"   - {key}: {value}")
                    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
