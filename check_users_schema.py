#!/usr/bin/env python
"""Check actual Supabase users table schema and sample data"""

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
print("CHECKING USERS TABLE SCHEMA")
print("=" * 80)

try:
    # Fetch all users to see all columns
    response = supabase.client.table('users').select('*').execute()
    
    if response.data:
        print(f"\n✅ Found {len(response.data)} users")
        
        # Get first user to see all columns
        user = response.data[0]
        print("\n📋 Sample User Object:")
        print("-" * 80)
        for key, value in sorted(user.items()):
            print(f"  {key:30} = {value}")
        
        print("\n📊 All Available Columns:")
        print("-" * 80)
        columns = list(user.keys())
        for i, col in enumerate(sorted(columns), 1):
            print(f"  {i:2}. {col}")
            
        # Check which columns have values across all users
        print("\n" + "=" * 80)
        print("COLUMN STATISTICS")
        print("=" * 80)
        
        all_columns = set()
        columns_with_values = {}
        
        for user_obj in response.data:
            all_columns.update(user_obj.keys())
            for key, value in user_obj.items():
                if value is not None:
                    if key not in columns_with_values:
                        columns_with_values[key] = 0
                    columns_with_values[key] += 1
        
        print(f"\n✅ Column Analysis (out of {len(response.data)} users):")
        print("-" * 80)
        for col in sorted(all_columns):
            count = columns_with_values.get(col, 0)
            status = "✅ HAS DATA" if count > 0 else "⚠️  NULL/EMPTY"
            print(f"  {col:30} : {status} ({count}/{len(response.data)} users)")
    else:
        print("\n❌ No users found")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
