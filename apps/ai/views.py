import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from apps.ai.services import AIService
from config.supabase_client import get_service


STANDARD_THRESHOLDS = {
    "pm25": {"minimum": 0, "maximum": 12},
    "pm10": {"minimum": 0, "maximum": 54},
    "co2": {"minimum": 0, "maximum": 1000},
}

PREDICTION_PARAMETER_MAP = {
    "temperatura": "temperature",
    "umiditate": "humidity",
    "co2": "co2",
    "pm25": "pm25",
    "pm10": "pm10",
    "voc": "voc",
}


def evaluate_prediction_profile(payload, device_id, user_id):
    """Compare prediction inputs to the selected device's active profile thresholds."""
    profile = get_service().get_transport_profile(device_id, user_id)
    thresholds = profile.get("thresholds", {}) if profile else STANDARD_THRESHOLDS
    checks = []
    for parameter, threshold in thresholds.items():
        value = payload.get(PREDICTION_PARAMETER_MAP.get(parameter, parameter))
        if not isinstance(value, (int, float)):
            continue
        minimum = float(threshold["minimum"])
        maximum = float(threshold["maximum"])
        if value < minimum:
            label = "sub_minim"
        elif value > maximum:
            label = "peste_maxim"
        else:
            label = "in_interval"
        checks.append({
            "parameter": parameter,
            "value": value,
            "minimum": minimum,
            "maximum": maximum,
            "in_range": label == "in_interval",
            "label": label,
        })
    return {
        "profile_name": profile.get("profile_name") if profile else "Standard",
        "is_standard": profile is None,
        "checks": checks,
        "in_range": all(check["in_range"] for check in checks) if checks else None,
    }


def ai_status(request):
    return render(request, "ai/interface.html")


def ai_interface(request):
    """Comprehensive AI interface with chat, prediction, training, and anomaly detection"""
    return render(request, "ai/interface.html")


@require_GET
def user_devices(request):
    """Return only the authenticated user's devices for the AI selector."""
    user_id = request.session.get("supabase_user_id")
    if not user_id:
        return JsonResponse({"detail": "Autentificarea este necesara."}, status=401)

    devices = get_service().get_user_devices(user_id)
    return JsonResponse(
        {
            "devices": [
                {
                    "id": device.get("device_id") or device.get("id"),
                    "name": device.get("name") or device.get("device_id") or device.get("id"),
                }
                for device in devices
                if device.get("device_id") or device.get("id")
            ]
        }
    )


def _json_payload(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@require_POST
def train(request):
    payload = _json_payload(request)
    if payload is None:
        return JsonResponse({"detail": "JSON invalid."}, status=400)
    return JsonResponse(AIService().train(payload))


@require_POST
def predict(request):
    payload = _json_payload(request)
    if payload is None:
        return JsonResponse({"detail": "JSON invalid."}, status=400)
    user_id = request.session.get("supabase_user_id")
    device_id = payload.get("device_id")
    prediction = AIService().predict(payload)
    if user_id and device_id:
        prediction["profile_evaluation"] = evaluate_prediction_profile(payload, device_id, user_id)
    return JsonResponse(prediction)


@require_POST
def anomaly(request):
    payload = _json_payload(request)
    if payload is None:
        return JsonResponse({"detail": "JSON invalid."}, status=400)
    return JsonResponse(AIService().detect_anomalies(payload))


@require_POST
def chat(request):
    payload = _json_payload(request)
    if not isinstance(payload, dict) or not isinstance(payload.get("message"), str):
        return JsonResponse({"detail": "Campul message este obligatoriu."}, status=400)
    return JsonResponse(AIService().chat(payload["message"]))