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


@require_http_methods(["GET", "POST"])
def transport_profile(request, device_id):
    """Configure client-owned temperature limits for a device's cargo."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return redirect("qr_login:start")

    supabase = get_service()
    device = supabase.get_device(device_id, user_id)
    if not device:
        return render(
            request,
            "devices/transport_profile.html",
            {"error": "Dispozitivul nu a fost gasit sau nu iti apartine."},
            status=404,
        )

    profile = supabase.get_transport_profile(device_id, user_id)
    form_data = {
        "profile_name": (profile or {}).get("profile_name", ""),
        "cargo_name": (profile or {}).get("cargo_name", ""),
        "minimum_temperature": (profile or {}).get("minimum_temperature", ""),
        "maximum_temperature": (profile or {}).get("maximum_temperature", ""),
        "notes": (profile or {}).get("notes", ""),
    }

    if request.method == "POST":
        form_data = {
            "profile_name": request.POST.get("profile_name", "").strip(),
            "cargo_name": request.POST.get("cargo_name", "").strip(),
            "minimum_temperature": request.POST.get("minimum_temperature", "").strip(),
            "maximum_temperature": request.POST.get("maximum_temperature", "").strip(),
            "notes": request.POST.get("notes", "").strip(),
        }
        try:
            minimum_temperature = float(form_data["minimum_temperature"])
            maximum_temperature = float(form_data["maximum_temperature"])
            if not form_data["profile_name"]:
                raise ValueError("Introdu un nume pentru profil.")
            if not form_data["cargo_name"]:
                raise ValueError("Introdu marfa transportata.")
            if not -50 <= minimum_temperature <= 80 or not -50 <= maximum_temperature <= 80:
                raise ValueError("Temperaturile trebuie sa fie intre -50 si 80 °C.")
            if minimum_temperature >= maximum_temperature:
                raise ValueError("Temperatura minima trebuie sa fie mai mica decat temperatura maxima.")
        except ValueError as error:
            return render(
                request,
                "devices/transport_profile.html",
                {"device": device, "form_data": form_data, "error": str(error)},
                status=400,
            )

        saved_profile = supabase.save_transport_profile(
            device_id,
            user_id,
            form_data["profile_name"],
            form_data["cargo_name"],
            minimum_temperature,
            maximum_temperature,
            form_data["notes"],
        )
        if not saved_profile:
            return render(
                request,
                "devices/transport_profile.html",
                {"device": device, "form_data": form_data, "error": "Profilul nu a putut fi salvat."},
                status=500,
            )
        profile = saved_profile
        form_data = {
            "profile_name": profile.get("profile_name", ""),
            "cargo_name": profile.get("cargo_name", ""),
            "minimum_temperature": profile.get("minimum_temperature", ""),
            "maximum_temperature": profile.get("maximum_temperature", ""),
            "notes": profile.get("notes", ""),
        }
        return render(
            request,
            "devices/transport_profile.html",
            {"device": device, "form_data": form_data, "success": "Profilul de transport a fost salvat."},
        )

    return render(request, "devices/transport_profile.html", {"device": device, "form_data": form_data})


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
