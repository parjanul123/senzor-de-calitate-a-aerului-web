"""
Measurements views.
"""

import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from apps.measurements.services import get_device_measurements, get_latest_measurement
from config.supabase_client import get_service


@require_http_methods(["GET"])
def history(request, device_id):
    """View measurement history for a device."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return redirect("qr_login:start")
    
    try:
        limit = request.GET.get("limit", 100)
        data = get_device_measurements(device_id, user_id, limit=int(limit))
        
        if "error" in data:
            return render(request, "measurements/history.html", data, status=404)
        
        return render(request, "measurements/history.html", data)
    except Exception as e:
        return render(
            request,
            "measurements/history.html",
            {"error": f"Error loading history: {str(e)}", "measurements": []},
            status=500
        )


@require_http_methods(["GET"])
def charts(request, device_id):
    """View charts for a device (redirects to device dashboard)."""
    return redirect("dashboard_device", device_id=device_id)


@require_http_methods(["GET"])
def latest_data(request, device_id):
    """API endpoint to get latest measurement as JSON."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    
    try:
        measurement = get_latest_measurement(device_id, user_id)
        if not measurement:
            return JsonResponse({"error": "No measurements found"}, status=404)
        
        return JsonResponse(measurement)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def measurement_detail(request, device_id, metric):
    """View detailed chart for a specific measurement with zoom capability."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return redirect("qr_login:start")
    
    try:
        supabase = get_service()
        
        # Verify device belongs to user
        device = supabase.get_device(device_id, user_id)
        if not device:
            return render(request, "measurements/detail.html", {"error": "Device not found"}, status=404)
        
        # Fetch measurements for chart
        measurements = supabase.get_device_measurements(device_id, user_id, limit=1000)
        
        # Extract data for specific metric
        timestamps = [m.get("created_at", "") for m in measurements]
        values = [m.get(metric) for m in measurements]
        
        # Metric labels and colors
        metric_labels = {
            "temperatura": {"label": "Temperatură", "unit": "°C", "color": "#ff6b6b"},
            "umiditate": {"label": "Umiditate", "unit": "%", "color": "#4ecdc4"},
            "presiune": {"label": "Presiune", "unit": "hPa", "color": "#95a5a6"},
            "co2": {"label": "CO₂", "unit": "ppm", "color": "#f39c12"},
            "pm1": {"label": "PM1.0", "unit": "μg/m³", "color": "#3498db"},
            "pm25": {"label": "PM2.5", "unit": "μg/m³", "color": "#e74c3c"},
            "pm10": {"label": "PM10", "unit": "μg/m³", "color": "#e67e22"},
            "voc": {"label": "VOC", "unit": "ppb", "color": "#9b59b6"},
            "lux": {"label": "Lux", "unit": "lux", "color": "#f1c40f"},
        }
        
        metric_info = metric_labels.get(metric, {"label": metric, "unit": "", "color": "#95a5a6"})
        
        return render(request, "measurements/detail.html", {
            "device": device,
            "metric": metric,
            "metric_label": metric_info["label"],
            "metric_unit": metric_info["unit"],
            "metric_color": metric_info["color"],
            "timestamps": json.dumps(timestamps),
            "values": json.dumps(values),
            "user_id": user_id,
        })
    except Exception as e:
        return render(
            request,
            "measurements/detail.html",
            {"error": f"Error loading chart: {str(e)}"},
            status=500
        )
