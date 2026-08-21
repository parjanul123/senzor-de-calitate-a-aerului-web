"""
Device views.
"""

import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from apps.devices.services import get_user_devices, get_device_detail
from config.supabase_client import get_service


@require_http_methods(["GET"])
def devices(request):
    """List all devices for the authenticated user."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return redirect("qr_login:start")
    
    try:
        devices = get_user_devices(user_id)
        return render(request, "devices/index.html", {"devices": devices})
    except Exception as e:
        return render(
            request,
            "devices/index.html",
            {"error": f"Error loading devices: {str(e)}", "devices": []},
            status=500
        )


@require_http_methods(["POST"])
def update_device_location(request):
    """API endpoint to update device location."""
    user_id = request.session.get("supabase_user_id")
    
    if not user_id:
        return JsonResponse(
            {"success": False, "error": "Not authenticated"},
            status=401
        )
    
    try:
        data = json.loads(request.body)
        device_id = data.get("device_id")
        location = data.get("location", "").strip()
        
        if not device_id:
            return JsonResponse(
                {"success": False, "error": "device_id is required"},
                status=400
            )
        
        if not location:
            return JsonResponse(
                {"success": False, "error": "location is required"},
                status=400
            )
        
        supabase = get_service()
        success = supabase.update_device_location(device_id, user_id, location)
        
        if success:
            return JsonResponse({
                "success": True,
                "message": "Location updated successfully",
                "device_id": device_id,
                "location": location
            })
        else:
            return JsonResponse(
                {"success": False, "error": "Failed to update location"},
                status=500
            )
    
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=500
        )
