import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from apps.ai.services import AIService
from config.supabase_client import get_service


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
    return JsonResponse(AIService().predict(payload))


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