#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.devices.services import get_user_devices

user_id = '3026d270-2ecb-4c61-8724-70573c28be47'
devices_data = get_user_devices(user_id)

print("Current devices and locations:")
for item in devices_data:
    device = item['device']
    device_id = device.get('device_id', 'N/A')
    location = device.get('location', 'No location set')
    print(f"  Device: {device_id}")
    print(f"  Location: {location}")
    print()
