import json
import logging
import re

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods

from config.supabase_client import get_service

logger = logging.getLogger(__name__)


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._\-\s]+$")
RESERVED_USERNAMES = {
    "admin",
    "administrator",
    "root",
    "system",
    "support",
    "null",
    "undefined",
}


def profile(request):
    """Display user profile with all available data from Supabase and session."""
    
    supabase_user_id = request.session.get("supabase_user_id")
    authenticated_at = request.session.get("supabase_authenticated_at")
    qr_login_request_id = request.session.get("qr_login_request_id")
    
    supabase = get_service()
    
    # Load username from Supabase users table (source of truth)
    username = None
    if supabase_user_id:
        try:
            username = supabase.get_username(supabase_user_id)
            if username is None:
                user_record = supabase.get_user(supabase_user_id)
                if user_record:
                    username = user_record.get("username")
        except Exception as e:
            print(f"Error fetching username from Supabase: {e}")

    logger.info("[profile] resolved username for user %s: %r", supabase_user_id, username)
    username_is_set = bool(isinstance(username, str) and username.strip())
    request.session["username_set"] = username_is_set
    request.session["username_checked_for"] = supabase_user_id
    
    # Fetch all user devices
    user_devices = []
    if supabase_user_id:
        try:
            response = supabase.get_user_devices(supabase_user_id)
            user_devices = response if response else []
        except Exception as e:
            print(f"Error fetching devices: {e}")
    
    # Fetch QR login request details if available
    qr_login_data = None
    if qr_login_request_id:
        try:
            response = supabase.get_login_request(qr_login_request_id)
            qr_login_data = response
        except Exception as e:
            print(f"Error fetching QR login data: {e}")
    
    # Parse authenticated_at if it's a string
    auth_datetime = None
    if authenticated_at:
        if isinstance(authenticated_at, str):
            auth_datetime = parse_datetime(authenticated_at)
        else:
            auth_datetime = authenticated_at
    
    # Build session data for display
    session_data = {
        "supabase_user_id": supabase_user_id,
        "qr_login_request_id": qr_login_request_id,
        "authenticated_at": str(authenticated_at),
        "session_expiry": request.session.get("_session_expiry"),
    }
    
    return render(
        request,
        "accounts/profile.html",
        {
            "supabase_user_id": supabase_user_id,
            "authenticated_at": auth_datetime or authenticated_at,
            "qr_login_request_id": qr_login_request_id,
            "qr_login_data": qr_login_data,
            "username": username,
            "username_is_set": username_is_set,
            "user_devices": user_devices,
            "device_count": len(user_devices),
            "session_data": json.dumps(session_data, indent=2),
        },
    )


@require_http_methods(["POST", "PUT"])
def manage_username(request):
    """API endpoint to save or update username in Supabase users table."""
    
    supabase_user_id = request.session.get("supabase_user_id")
    
    if not supabase_user_id:
        return JsonResponse(
            {"success": False, "error": "Not authenticated"},
            status=401
        )
    
    try:
        if request.content_type and "application/json" not in request.content_type:
            return JsonResponse(
                {"success": False, "error": "Content-Type must be application/json"},
                status=415,
            )

        if len(request.body or b"") > 1024:
            return JsonResponse(
                {"success": False, "error": "Payload too large"},
                status=413,
            )

        data = json.loads(request.body)
        raw_username = data.get("username", "")

        if not isinstance(raw_username, str):
            return JsonResponse(
                {"success": False, "error": "Username must be a string"},
                status=400,
            )

        username = raw_username.strip()
        
        if not username:
            return JsonResponse(
                {"success": False, "error": "Username cannot be empty"},
                status=400
            )
        
        if len(username) < 3 or len(username) > 50:
            return JsonResponse(
                {"success": False, "error": "Username must be between 3 and 50 characters"},
                status=400
            )

        if username.lower() in RESERVED_USERNAMES:
            return JsonResponse(
                {"success": False, "error": "This username is reserved"},
                status=400,
            )

        if "  " in username:
            return JsonResponse(
                {"success": False, "error": "Username cannot contain consecutive spaces"},
                status=400,
            )

        if not USERNAME_PATTERN.fullmatch(username):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Username may contain letters, numbers, spaces, '.', '_' and '-' only",
                },
                status=400,
            )
        
        supabase = get_service()

        existing_user = supabase.get_user(supabase_user_id)
        if existing_user:
            supabase.update_user(supabase_user_id, username)
        else:
            supabase.create_user(supabase_user_id, username)

        request.session["username_set"] = True
        request.session["username_checked_for"] = supabase_user_id

        return JsonResponse({
            "success": True,
            "message": "Username saved successfully",
            "username": username,
        })
        
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        print(f"Error managing username: {e}")
        return JsonResponse(
            {"success": False, "error": "Nu am putut salva username-ul in baza de date."},
            status=500
        )


@require_http_methods(["POST"])
def set_theme(request):
    """Persist UI theme preference in the user session."""
    try:
        if request.content_type and "application/json" not in request.content_type:
            return JsonResponse(
                {"success": False, "error": "Content-Type must be application/json"},
                status=415,
            )

        data = json.loads(request.body)
        theme = data.get("theme")
        if theme not in {"light", "dark"}:
            return JsonResponse(
                {"success": False, "error": "Theme must be either 'light' or 'dark'"},
                status=400,
            )

        request.session["ui_theme"] = theme
        request.session.modified = True
        return JsonResponse({"success": True, "theme": theme})
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400,
        )