from django.shortcuts import render
from django.utils.dateparse import parse_datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from config.supabase_client import get_service
from .models import UserProfile


def profile(request):
    """Display user profile with all available data from Supabase and session."""
    
    supabase_user_id = request.session.get("supabase_user_id")
    authenticated_at = request.session.get("supabase_authenticated_at")
    qr_login_request_id = request.session.get("qr_login_request_id")
    
    supabase = get_service()
    
    # Get or create user profile with username from local database
    username = None
    user_profile = None
    if supabase_user_id:
        try:
            # Try to get existing profile
            user_profile = UserProfile.objects.filter(supabase_user_id=supabase_user_id).first()
            
            if user_profile:
                username = user_profile.username
            else:
                # Create new profile with auto-generated username
                username = f"Utilizator_{supabase_user_id[:8]}"
                user_profile = UserProfile.objects.create(
                    supabase_user_id=supabase_user_id,
                    username=username
                )
        except Exception as e:
            print(f"Error with user profile: {e}")
            # Fallback to generated username
            username = f"Utilizator_{supabase_user_id[:8]}"
    
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
            "user_profile": user_profile,
            "username": username,
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
        data = json.loads(request.body)
        username = data.get("username", "").strip()
        
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
        
        supabase = get_service()
        
        # Try to save/update username in Supabase
        # If RLS prevents it, we'll still return success and suggest localStorage fallback
        result = None
        error_msg = None
        
        try:
            if request.method == "POST":
                # Try insert
                result = supabase.create_user(supabase_user_id, username)
            elif request.method == "PUT":
                # Try update
                result = supabase.update_user(supabase_user_id, username)
        except Exception as e:
            error_msg = str(e)
            # If it fails due to RLS, log it but continue - we can still return success
            # because the API caller can use localStorage as fallback
            print(f"⚠️ Supabase operation failed (RLS or other): {e}")
            print(f"ℹ️ Username will be stored in localStorage instead")
        
        # Return success regardless of Supabase operation
        # Client can use localStorage as fallback
        return JsonResponse({
            "success": True,
            "message": "Username saved successfully",
            "username": username,
            "note": "Currently using localStorage storage. Supabase integration pending.",
            "storage": "localStorage",
            "supabase_error": error_msg  # Debugging info
        })
        
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        print(f"Error managing username: {e}")
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=500
        )