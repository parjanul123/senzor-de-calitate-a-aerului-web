#!/usr/bin/env python
"""Check actual Supabase measurements table schema and sample data"""

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

# Fetch one measurement to see all columns
print("=" * 80)
print("CHECKING MEASUREMENTS TABLE SCHEMA")
print("=" * 80)

try:
    # Fetch one measurement for device AQM-44C6EEC40A24
    response = supabase.client.table('measurements').select('*').eq('device_id', 'AQM-44C6EEC40A24').limit(1).execute()
    
    if response.data:
        measurement = response.data[0]
        print("\n✅ Sample Measurement Object:")
        print("-" * 80)
        for key, value in sorted(measurement.items()):
            print(f"  {key:30} = {value}")
        
        print("\n📊 All Available Columns:")
        print("-" * 80)
        columns = list(measurement.keys())
        for i, col in enumerate(sorted(columns), 1):
            print(f"  {i:2}. {col}")
    else:
        print("\n❌ No measurements found for device AQM-44C6EEC40A24")
        
    # Fetch multiple measurements to check if all have same columns
    print("\n" + "=" * 80)
    print("CHECKING MULTIPLE MEASUREMENTS")
    print("=" * 80)
    
    response = supabase.client.table('measurements').select('*').eq('device_id', 'AQM-44C6EEC40A24').limit(5).execute()
    
    if response.data:
        print(f"\n✅ Found {len(response.data)} measurements")
        
        # Check which columns have values
        all_columns = set()
        columns_with_values = {}
        
        for measurement in response.data:
            all_columns.update(measurement.keys())
            for key, value in measurement.items():
                if value is not None:
                    if key not in columns_with_values:
                        columns_with_values[key] = 0
                    columns_with_values[key] += 1
        
        print("\n📊 Column Analysis (out of 5 measurements):")
        print("-" * 80)
        for col in sorted(all_columns):
            count = columns_with_values.get(col, 0)
            status = "✅ HAS DATA" if count > 0 else "⚠️  NULL/EMPTY"
            print(f"  {col:30} : {status} ({count}/5 measurements)")
            
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
