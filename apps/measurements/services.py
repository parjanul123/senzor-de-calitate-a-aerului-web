"""
Measurement services for fetching data from Supabase.
"""

from config.supabase_client import get_service


def get_device_measurements(device_id: str, user_id: str, limit: int = 100) -> dict:
    """
    Get measurements for a specific device.
    """
    supabase = get_service()
    
    # Verify device belongs to user
    device = supabase.get_device(device_id, user_id)
    if not device:
        return {"error": "Device not found"}
    
    measurements = supabase.get_device_measurements(device_id, user_id, limit=limit)
    
    return {
        "device": device,
        "measurements": measurements,
        "count": len(measurements),
    }


def get_latest_measurement(device_id: str, user_id: str) -> dict:
    """
    Get the latest measurement for a device.
    """
    supabase = get_service()
    
    measurement = supabase.get_latest_measurement(device_id, user_id)
    return measurement if measurement else {}