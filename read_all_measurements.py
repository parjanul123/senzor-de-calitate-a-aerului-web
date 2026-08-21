#!/usr/bin/env python
"""Read ALL data from Supabase measurements table"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

import django
django.setup()

from config.supabase_client import get_service
import json
from datetime import datetime

supabase = get_service()

print("=" * 100)
print("READING ALL DATA FROM SUPABASE MEASUREMENTS TABLE")
print("=" * 100)

try:
    # Fetch ALL measurements (no limit)
    response = supabase.client.table('measurements').select('*').order('created_at', desc=True).execute()
    
    measurements = response.data if response.data else []
    
    print(f"\n✅ Total measurements found: {len(measurements)}")
    
    if measurements:
        print("\n" + "=" * 100)
        print("SUMMARY STATISTICS")
        print("=" * 100)
        
        # Group by device_id
        by_device = {}
        for m in measurements:
            device_id = m.get('device_id', 'unknown')
            if device_id not in by_device:
                by_device[device_id] = []
            by_device[device_id].append(m)
        
        print(f"\n📊 Devices: {len(by_device)}")
        for device_id, device_measurements in by_device.items():
            print(f"   - {device_id}: {len(device_measurements)} measurements")
        
        # Date range
        if measurements:
            oldest = measurements[-1].get('created_at')  # Last item (oldest due to desc order)
            newest = measurements[0].get('created_at')   # First item (newest)
            print(f"\n📅 Date Range:")
            print(f"   - Newest: {newest}")
            print(f"   - Oldest: {oldest}")
        
        # All columns
        all_columns = set()
        for m in measurements:
            all_columns.update(m.keys())
        
        print(f"\n📋 Available Columns ({len(all_columns)}):")
        for col in sorted(all_columns):
            print(f"   - {col}")
        
        # Display first 10 measurements
        print("\n" + "=" * 100)
        print("FIRST 10 MEASUREMENTS (NEWEST)")
        print("=" * 100)
        
        for i, measurement in enumerate(measurements[:10], 1):
            print(f"\n📍 Measurement #{i}:")
            print(f"   ID: {measurement.get('id')}")
            print(f"   Device: {measurement.get('device_id')}")
            print(f"   Created: {measurement.get('created_at')}")
            print(f"   Values:")
            print(f"      - Temperatura: {measurement.get('temperatura')}°C")
            print(f"      - Umiditate: {measurement.get('umiditate')}%")
            print(f"      - Presiune: {measurement.get('presiune')} hPa")
            print(f"      - CO₂: {measurement.get('co2')} ppm")
            print(f"      - PM1: {measurement.get('pm1')}")
            print(f"      - PM2.5: {measurement.get('pm25')}")
            print(f"      - PM10: {measurement.get('pm10')}")
            print(f"      - VOC: {measurement.get('voc')}")
            print(f"      - Lux: {measurement.get('lux')}")
        
        # Display last 10 measurements
        print("\n" + "=" * 100)
        print("LAST 10 MEASUREMENTS (OLDEST)")
        print("=" * 100)
        
        for i, measurement in enumerate(measurements[-10:], 1):
            print(f"\n📍 Measurement #{len(measurements)-10+i}:")
            print(f"   ID: {measurement.get('id')}")
            print(f"   Device: {measurement.get('device_id')}")
            print(f"   Created: {measurement.get('created_at')}")
            print(f"   Values:")
            print(f"      - Temperatura: {measurement.get('temperatura')}°C")
            print(f"      - Umiditate: {measurement.get('umiditate')}%")
            print(f"      - Presiune: {measurement.get('presiune')} hPa")
            print(f"      - CO₂: {measurement.get('co2')} ppm")
            print(f"      - PM1: {measurement.get('pm1')}")
            print(f"      - PM2.5: {measurement.get('pm25')}")
            print(f"      - PM10: {measurement.get('pm10')}")
            print(f"      - VOC: {measurement.get('voc')}")
            print(f"      - Lux: {measurement.get('lux')}")
        
        # Export to JSON
        print("\n" + "=" * 100)
        print("EXPORTING DATA TO JSON")
        print("=" * 100)
        
        json_file = "measurements_export.json"
        with open(json_file, 'w') as f:
            json.dump(measurements, f, indent=2, default=str)
        
        print(f"\n✅ Exported {len(measurements)} measurements to {json_file}")
        
        # Statistics per column
        print("\n" + "=" * 100)
        print("DETAILED COLUMN STATISTICS")
        print("=" * 100)
        
        numeric_cols = ['temperatura', 'umiditate', 'presiune', 'co2', 'pm1', 'pm25', 'pm10', 'voc', 'lux']
        
        for col in numeric_cols:
            values = [m.get(col) for m in measurements if m.get(col) is not None]
            if values:
                print(f"\n📊 {col}:")
                print(f"   - Count: {len(values)}")
                print(f"   - Min: {min(values)}")
                print(f"   - Max: {max(values)}")
                print(f"   - Avg: {sum(values) / len(values):.2f}")
                print(f"   - Null/Missing: {len(measurements) - len(values)}")
    else:
        print("\n❌ No measurements found!")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
