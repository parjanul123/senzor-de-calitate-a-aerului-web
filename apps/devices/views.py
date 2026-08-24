"""
Device views.
"""

import json
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from apps.ai.services import AIService
from apps.devices.services import get_user_devices, get_device_detail
from config.supabase_client import get_service


STANDARD_LIMITS = [
    {"label": "PM2.5", "minimum": 0, "maximum": 12, "unit": "μg/m³"},
    {"label": "PM10", "minimum": 0, "maximum": 54, "unit": "μg/m³"},
    {"label": "CO2", "minimum": 0, "maximum": 1000, "unit": "ppm"},
    {"label": "VOC", "minimum": 0, "maximum": 220, "unit": "ppb"},
]

PARAMETERS = [
    ("temperatura", "Temperatura", "°C"),
    ("umiditate", "Umiditate", "%"),
    ("co2", "CO2", "ppm"),
    ("pm25", "PM2.5", "μg/m³"),
    ("pm10", "PM10", "μg/m³"),
    ("voc", "VOC", "ppb"),
]

PARAMETER_DETAILS = {key: {"label": label, "unit": unit} for key, label, unit in PARAMETERS}


def empty_profile_form():
    """Provide one independently editable threshold pair for every sensor parameter."""
    return {"profile_name": "", "notes": "", "thresholds": {key: {"minimum": "", "maximum": ""} for key, _, _ in PARAMETERS}}


def parse_profile_form(request):
    """Validate any supplied min/max pairs and retain blank parameters as unset."""
    form_data = {
        "profile_name": request.POST.get("profile_name", "").strip(),
        "notes": request.POST.get("notes", "").strip(),
        "thresholds": {},
    }
    if not form_data["profile_name"]:
        raise ValueError("Introdu un nume pentru profil.")

    thresholds = {}
    for parameter, _, _ in PARAMETERS:
        minimum = request.POST.get(f"minimum_{parameter}", "").strip()
        maximum = request.POST.get(f"maximum_{parameter}", "").strip()
        form_data["thresholds"][parameter] = {"minimum": minimum, "maximum": maximum}
        if not minimum and not maximum:
            continue
        if not minimum or not maximum:
            raise ValueError(f"Completeaza ambele praguri pentru {PARAMETER_DETAILS[parameter]['label']}.")
        minimum_value = float(minimum)
        maximum_value = float(maximum)
        if minimum_value >= maximum_value:
            raise ValueError(f"Pragul minim trebuie sa fie mai mic decat pragul maxim pentru {PARAMETER_DETAILS[parameter]['label']}.")
        thresholds[parameter] = {"minimum": minimum_value, "maximum": maximum_value}

    if not thresholds:
        raise ValueError("Seteaza cel putin un prag pentru un parametru.")
    return form_data, thresholds


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
    """List and configure standard or custom parameter profiles for a device."""
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

    profiles = supabase.get_transport_profiles(device_id, user_id)
    standard_active = not any(profile.get("is_active") for profile in profiles)
    editing_profile = next((profile for profile in profiles if str(profile.get("id")) == request.GET.get("edit")), None)
    form_data = empty_profile_form()
    if editing_profile:
        form_data["profile_name"] = editing_profile.get("profile_name", "")
        form_data["notes"] = editing_profile.get("notes", "")
        for parameter, threshold in editing_profile.get("thresholds", {}).items():
            if parameter in form_data["thresholds"]:
                form_data["thresholds"][parameter] = threshold

    def page_context(**extra):
        for profile in profiles:
            profile["threshold_items"] = [
                {"label": PARAMETER_DETAILS[key]["label"], "unit": PARAMETER_DETAILS[key]["unit"], **value}
                for key, value in profile.get("thresholds", {}).items() if key in PARAMETER_DETAILS
            ]
        parameter_fields = [
            {
                "key": key,
                "label": label,
                "unit": unit,
                "minimum": form_data["thresholds"].get(key, {}).get("minimum", ""),
                "maximum": form_data["thresholds"].get(key, {}).get("maximum", ""),
            }
            for key, label, unit in PARAMETERS
        ]
        return {
            "device": device, "form_data": form_data, "profiles": profiles,
            "standard_limits": STANDARD_LIMITS, "parameters": PARAMETERS,
            "parameter_fields": parameter_fields, "editing_profile": editing_profile,
            "standard_active": standard_active, **extra,
        }

    if request.method == "POST":
        action = request.POST.get("action", "create")
        if action == "activate":
            success = supabase.activate_transport_profile(device_id, request.POST.get("profile_id", ""), user_id)
            return redirect("devices:transport_profile", device_id=device_id) if success else render(request, "devices/transport_profile.html", page_context(error="Profilul nu a putut fi activat."), status=400)
        if action == "activate_standard":
            success = supabase.activate_standard_transport_profile(device_id, user_id)
            return redirect("devices:transport_profile", device_id=device_id) if success else render(request, "devices/transport_profile.html", page_context(error="Profilul Standard nu a putut fi activat."), status=400)
        if action == "delete":
            success = supabase.delete_transport_profile(device_id, request.POST.get("profile_id", ""), user_id)
            return redirect("devices:transport_profile", device_id=device_id) if success else render(request, "devices/transport_profile.html", page_context(error="Profilul nu a putut fi sters."), status=400)
        try:
            form_data, thresholds = parse_profile_form(request)
        except ValueError as error:
            return render(request, "devices/transport_profile.html", page_context(error=str(error)), status=400)

        if action == "edit":
            saved_profile = supabase.update_transport_profile(device_id, request.POST.get("profile_id", ""), user_id, form_data["profile_name"], thresholds, form_data["notes"])
        else:
            saved_profile = supabase.save_transport_profile(device_id, user_id, form_data["profile_name"], thresholds, form_data["notes"])
        if not saved_profile:
            return render(
                request,
                "devices/transport_profile.html",
                page_context(error="Supabase blocheaza modificarea prin politica RLS pentru tabela profiles. Verifica politicile INSERT, UPDATE si DELETE."), status=403,
            )
        return redirect("devices:transport_profile", device_id=device_id)

    return render(request, "devices/transport_profile.html", page_context())


@require_http_methods(["GET"])
def transport_profile_data(request, device_id):
    """Return the active profile thresholds for client-side prediction labeling."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return JsonResponse({"detail": "Autentificarea este necesara."}, status=401)

    supabase = get_service()
    if not supabase.get_device(device_id, user_id):
        return JsonResponse({"detail": "Dispozitivul nu a fost gasit."}, status=404)

    profile = supabase.get_transport_profile(device_id, user_id)
    if profile:
        return JsonResponse({
            "profile_name": profile.get("profile_name"),
            "thresholds": profile.get("thresholds", {}),
        })
    return JsonResponse({
        "profile_name": "Standard",
        "thresholds": {
            "pm25": {"minimum": 0, "maximum": 12},
            "pm10": {"minimum": 0, "maximum": 54},
            "co2": {"minimum": 0, "maximum": 1000},
        },
    })


@require_http_methods(["GET"])
def transport_profile_suggestions(request, device_id):
    """Return AI suggestions for threshold configuration based on entered profile name."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return JsonResponse({"success": False, "error": "Autentificarea este necesara."}, status=401)

    supabase = get_service()
    device = supabase.get_device(device_id, user_id)
    if not device:
        return JsonResponse({"success": False, "error": "Dispozitivul nu a fost gasit."}, status=404)

    profile_name = (request.GET.get("profile_name") or "").strip()
    if not profile_name:
        return JsonResponse(
            {
                "success": False,
                "error": "Completeaza numele profilului, apoi cere sugestii AI.",
            },
            status=400,
        )

    search_goal = (request.GET.get("search_goal") or "").strip()
    operation_mode = (request.GET.get("operation_mode") or "general").strip().lower()
    if operation_mode not in {"general", "depozitare", "transport"}:
        operation_mode = "general"

    suggestion = AIService().recommend_transport_thresholds(
        profile_name=profile_name,
        device_name=device.get("name"),
        search_goal=search_goal,
        operation_mode=operation_mode,
    )
    return JsonResponse({"success": True, "suggestion": suggestion})


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
