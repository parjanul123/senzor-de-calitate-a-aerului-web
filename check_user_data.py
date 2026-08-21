#!/usr/bin/env python
"""Check user data in correct Supabase tables"""

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
print("CHECKING SUPABASE TABLES FOR USER DATA")
print("=" * 100)

# Check web_login_requests (correct table name)
print("\n🔍 Table: web_login_requests")
try:
    response = supabase.client.table('web_login_requests').select('*').limit(3).execute()
    if response.data:
        print(f"✅ Found {len(response.data)} records:")
        for i, record in enumerate(response.data, 1):
            print(f"\n   Record {i}:")
            for key, value in record.items():
                print(f"      - {key}: {value}")
    else:
        print("❌ No records found")
except Exception as e:
    print(f"❌ Error: {e}")

# Check users table
print("\n🔍 Table: users")
try:
    response = supabase.client.table('users').select('*').limit(3).execute()
    if response.data:
        print(f"✅ Found {len(response.data)} records:")
        for i, record in enumerate(response.data, 1):
            print(f"\n   Record {i}:")
            for key, value in record.items():
                print(f"      - {key}: {value}")
    else:
        print("❌ No records found in users table")
except Exception as e:
    print(f"❌ Error: {e}")

# Try to get Supabase auth user info
print("\n🔍 Supabase Auth Info")
try:
    # Get session from Django
    from django.contrib.sessions.models import Session
    from django.test import Client
    
    client = Client()
    response = client.get('/profile/')
    
    print(f"✅ Profile page status: {response.status_code}")
    
except Exception as e:
    print(f"⚠️  Cannot check auth: {e}")

# List all available tables
print("\n🔍 Available Tables in Supabase")
print("=" * 100)
try:
    # Try to query information_schema
    response = supabase.client.table('information_schema.tables').select('table_name').eq('table_schema', 'public').execute()
    print(f"Tables found:")
    for row in response.data:
        print(f"   - {row.get('table_name')}")
except Exception as e:
    # If that doesn't work, manually test common table names
    print("Testing common table names:")
    common_tables = ['users', 'profiles', 'accounts', 'web_login_requests', 'devices', 'measurements']
    for table_name in common_tables:
        try:
            response = supabase.client.table(table_name).select('*').limit(1).execute()
            print(f"   ✅ {table_name}: exists ({len(response.data)} sample records)")
        except:
            print(f"   ❌ {table_name}: not found or error")

print("\n" + "=" * 100)
