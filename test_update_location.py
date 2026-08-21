#!/usr/bin/env python
"""Test the location update endpoint"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from config.supabase_client import get_service

supabase = get_service()

# Test update
device_id = 'AQM-44C6EEC40A24'
user_id = '3026d270-2ecb-4c61-8724-70573c28be47'
location = 'Birou'

print(f"Testing location update:")
print(f"  Device: {device_id}")
print(f"  User: {user_id}")
print(f"  Location: {location}")
print()

success = supabase.update_device_location(device_id, user_id, location)
print(f"Update result: {success}")
print()

# Verify the update
print("Verifying...")
from apps.devices.services import get_user_devices
devices_data = get_user_devices(user_id)
for item in devices_data:
    device = item['device']
    if device.get('device_id') == device_id:
        new_location = device.get('location', 'No location')
        print(f"Device {device_id} location is now: {new_location}")
