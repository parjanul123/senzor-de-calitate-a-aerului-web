"""
Device services for fetching data from Supabase.
"""

from config.supabase_client import get_service


def get_user_devices(user_id: str) -> list:
    """
    Get all devices for a user with their latest measurements.
    """
    supabase = get_service()
    
    devices = supabase.get_user_devices(user_id)
    
    # Enhance each device with latest measurement
    devices_with_data = []
    for device in devices:
        latest_measurement = supabase.get_latest_measurement(device["device_id"], user_id)
        devices_with_data.append({
            "device": device,
            "latest_measurement": latest_measurement,
        })
    
    return devices_with_data


def get_device_detail(device_id: str, user_id: str) -> dict:
    """
    Get detailed information about a specific device.
    """
    supabase = get_service()
    
    device = supabase.get_device(device_id, user_id)
    if not device:
        return None
    
    latest_measurement = supabase.get_latest_measurement(device_id, user_id)
    
    return {
        "device": device,
        "latest_measurement": latest_measurement,
    }