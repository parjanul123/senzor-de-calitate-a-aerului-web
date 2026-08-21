#!/usr/bin/env python
"""List all tables and check users table with current user ID"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from config.supabase_client import get_service

# Get Supabase service
supabase = get_service()

print("=" * 80)
print("CHECKING SUPABASE TABLES & USERS DATA")
print("=" * 80)

# First, try to get info about tables by querying specific known tables
tables_to_check = ['users', 'auth.users', 'public.users', 'devices', 'measurements', 'web_login_requests']

print("\n📋 Checking Tables:")
print("-" * 80)

for table_name in tables_to_check:
    try:
        response = supabase.client.table(table_name).select('*').limit(1).execute()
        count = len(response.data) if response.data else 0
        print(f"  {table_name:30} : ✅ EXISTS ({count} records)")
    except Exception as e:
        print(f"  {table_name:30} : ❌ Error or not found")

# Try to get the specific user by ID (from session)
print("\n" + "=" * 80)
print("CHECKING CURRENT USER DATA")
print("=" * 80)

# The user ID from my test device
user_id = '3026d270-2ecb-4c61-8724-70573c28be47'

print(f"\nUser ID: {user_id}")
print("-" * 80)

# Try different table names
for table_name in ['users', 'public.users', 'auth.users']:
    try:
        response = supabase.client.table(table_name).select('*').eq('id', user_id).execute()
        
        if response.data:
            user = response.data[0]
            print(f"\n✅ Found in table: {table_name}")
            print("\n📋 User Data:")
            print("-" * 80)
            for key, value in sorted(user.items()):
                print(f"  {key:30} = {value}")
            break
    except Exception as e:
        continue

# Also check if users table has any data at all by a different approach
print("\n" + "=" * 80)
print("CHECKING RAW USERS TABLE")
print("=" * 80)

try:
    response = supabase.client.table('users').select('*').limit(10).execute()
    
    if response.data:
        print(f"\n✅ Found {len(response.data)} users:")
        print("-" * 80)
        for user in response.data:
            print(f"  ID: {user.get('id', 'N/A'):40} | Email: {user.get('email', 'N/A')}")
    else:
        print("\n❌ No users found in users table")
        
except Exception as e:
    print(f"\n❌ Error accessing users table: {e}")

print("\n" + "=" * 80)
