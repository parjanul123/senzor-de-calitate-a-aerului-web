#!/usr/bin/env python
"""Test updating location to Living"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from config.supabase_client import get_service
from apps.devices.services import get_user_devices

supabase = get_service()

# Update location
device_id = 'AQM-44C6EEC40A24'
user_id = '3026d270-2ecb-4c61-8724-70573c28be47'
new_location = 'Living'

print(f"Updating device location to: {new_location}")
success = supabase.update_device_location(device_id, user_id, new_location)
print(f"Update successful: {success}")
print()

# Verify
print("Checking updated location:")
devices_data = get_user_devices(user_id)
for item in devices_data:
    device = item['device']
    if device.get('device_id') == device_id:
        location = device.get('location', 'N/A')
        print(f"Device {device_id}: Location = '{location}'")

