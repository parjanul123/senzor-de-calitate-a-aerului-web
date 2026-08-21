"""
Dashboard services for fetching data from Supabase.
"""

import logging
from config.supabase_client import get_service

logger = logging.getLogger(__name__)


def get_dashboard_data(user_id: str) -> dict:
    """
    Fetch all data needed for dashboard display.
    Returns users, devices, and latest measurements.
    """
    supabase = get_service()
    
    # Fetch user
    user = supabase.get_user(user_id)
    
    # Fetch all devices for user
    devices = supabase.get_user_devices(user_id)
    logger.debug(f"📱 Fetched {len(devices)} devices for dashboard")
    if devices:
        logger.debug(f"   First device keys: {list(devices[0].keys()) if isinstance(devices[0], dict) else 'not a dict'}")
    
    # For each device, get latest measurement
    devices_with_measurements = []
    for device in devices:
        # Ensure device is a dict and has 'device_id' key
        if not isinstance(device, dict):
            logger.warning(f"   ⚠️  Device is not a dict: {type(device)}")
            continue
        
        # Use device_id (not id) for Supabase devices table
        device_id = device.get("device_id")
        if not device_id:
            logger.warning(f"   ⚠️  Device has no 'device_id' key: {device}")
            continue
        
        latest_measurement = supabase.get_latest_measurement(device_id, user_id)
        devices_with_measurements.append({
            "device": device,
            "latest_measurement": latest_measurement,
        })
    
    return {
        "user": user,
        "devices": devices_with_measurements,
    }


def get_device_dashboard_data(device_id: str, user_id: str, limit: int = 1000) -> dict:
    """
    Fetch data for a single device dashboard with charts.
    """
    supabase = get_service()
    
    # Verify device belongs to user
    device = supabase.get_device(device_id, user_id)
    if not device:
        return None
    
    # Fetch measurements for charts
    measurements = supabase.get_measurements_for_dashboard(device_id, user_id, limit=limit)
    
    # Prepare data for Chart.js (format as JSON-serializable dicts)
    # Log available fields in first measurement
    if measurements:
        logger.debug(f"📊 First measurement keys: {list(measurements[0].keys())}")
    
    chart_data = {
        "timestamps": [m.get("created_at", "") for m in measurements],
        "temperature": [m.get("temperatura") for m in measurements],
        "humidity": [m.get("umiditate") for m in measurements],
        "pressure": [m.get("presiune") for m in measurements],
        "voc": [m.get("voc") for m in measurements],  # VOC
        "lux": [m.get("lux") for m in measurements],
        "co2": [m.get("co2") for m in measurements],
        "pm1": [m.get("pm1") for m in measurements],
        "pm25": [m.get("pm25") for m in measurements],
        "pm10": [m.get("pm10") for m in measurements],
    }
    
    # Get latest measurement for summary
    latest = measurements[-1] if measurements else None
    if latest:
        logger.debug(f"📊 Latest measurement keys: {list(latest.keys())}")
        logger.debug(f"📊 Latest measurement: {latest}")

    transport_profile = supabase.get_transport_profile(device_id, user_id)
    transport_status = {"state": "not_configured"}
    if transport_profile:
        temperature = (latest or {}).get("temperatura")
        if temperature is None:
            transport_status = {"state": "no_measurement"}
        else:
            minimum = float(transport_profile["minimum_temperature"])
            maximum = float(transport_profile["maximum_temperature"])
            transport_status = {
                "state": "in_range" if minimum <= float(temperature) <= maximum else "out_of_range",
                "temperature": float(temperature),
            }
    
    return {
        "device": device,
        "latest_measurement": latest,
        "measurements": measurements,
        "chart_data": chart_data,
        "transport_profile": transport_profile,
        "transport_status": transport_status,
    }
