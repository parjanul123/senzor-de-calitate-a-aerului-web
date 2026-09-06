"""
QR Code authentication views (Steam Guard / WhatsApp Web style).

Flow:
1. Browser opens /qr-login/
2. View creates login request in Supabase (generates token UUID)
3. View generates QR code containing token and renders HTML with polling/Realtime JS
4. Browser listens via JavaScript polling or Supabase Realtime (watching by id)
5. Mobile app scans QR, reads token, uses it to confirm user identity
6. Mobile app updates Supabase: status="approved", user_id=<user>, approved_at=now()
7. Browser detects change, creates session, redirects to dashboard

Database Table (Supabase):
    web_login_requests (
        id: UUID primary key,
        token: UUID (NOT NULL, encoded in QR code),
        status: "pending" | "approved" | "rejected" | "expired",
        user_id: UUID (NULL until approved),
        expires_at: timestamp,
        approved_at: timestamp (NULL until approved),
        created_at: timestamp
    )

Note:
- `id` is used for database queries and browser polling
- `token` is what goes in the QR code (what mobile app scans)
"""

import base64
import json
import logging
import uuid
from datetime import datetime, timedelta
from io import BytesIO

import qrcode
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import get_service

# Setup logging
logger = logging.getLogger(__name__)


def _make_qr_image_data(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=6,
    )
    qr.add_data(data, optimize=0)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{qr_base64}"


QR_LOGIN_EXPIRES_IN_SECONDS = 180


def _get_android_app_download_url(request):
    configured_url = getattr(settings, "ANDROID_APP_DOWNLOAD_URL", "")
    if configured_url:
        if configured_url.startswith("/"):
            absolute_url = request.build_absolute_uri(configured_url)
            if request.get_host().endswith(".up.railway.app"):
                return absolute_url.replace("http://", "https://", 1)
            return absolute_url
        return configured_url

    static_url = settings.STATIC_URL.rstrip("/").lstrip("/")
    absolute_url = request.build_absolute_uri(f"/{static_url}/download/app-debug.apk")
    if request.get_host().endswith(".up.railway.app"):
        return absolute_url.replace("http://", "https://", 1)
    return absolute_url


@require_http_methods(["GET"])
def download_app(request):
    android_app_download_url = _get_android_app_download_url(request)
    android_app_qr_image = _make_qr_image_data(android_app_download_url)

    return render(
        request,
        "qr_login/download_app.html",
        {
            "android_app_download_url": android_app_download_url,
            "android_app_qr_image": android_app_qr_image,
        },
    )


@require_http_methods(["GET"])
def start(request):
    """
    Display QR code for authentication.
    
    1. Create login request in Supabase (generates token UUID)
    2. Generate QR code containing token (not id)
    3. Render template with polling/Realtime setup
    
    Note: 
    - `id` is used internally for database queries
    - `token` is what goes in the QR code and what mobile app scans
    """
    logger.info("📲 [start] QR login page requested")

    android_app_download_url = _get_android_app_download_url(request)
    base_context = {
        "android_app_download_url": android_app_download_url,
    }
    
    supabase = get_service()
    
    # Calculate expiration from now
    now = timezone.now()
    expires_at = (now + timedelta(seconds=QR_LOGIN_EXPIRES_IN_SECONDS)).isoformat()
    
    logger.info(f"   Creating login request with expiry: {expires_at}")
    
    # Create login request in Supabase (generates token UUID)
    try:
        login_request = supabase.create_login_request(expires_at)
        if not login_request:
            logger.error("❌ [start] Failed to create login request in Supabase")
            return render(
                request,
                "qr_login/start.html",
                {**base_context, "error": "Failed to create login request"},
                status=500,
            )
    except Exception as e:
        logger.error(f"❌ [start] Database error: {str(e)}")
        return render(
            request,
            "qr_login/start.html",
            {**base_context, "error": f"Database error: {str(e)}"},
            status=500,
        )
    
    # Extract id and token
    request_id = login_request["id"]
    token = login_request["token"]
    
    logger.info(f"✅ [start] Login request created")
    logger.info(f"   Request ID: {request_id}")
    logger.info(f"   Token (QR data): {token}")
    
    # Generate QR code containing TOKEN (what mobile app scans)
    qr_data = str(token)
    
    logger.info(f"   Generating QR code with data: {qr_data}")
    
    try:
        qr_image_data = _make_qr_image_data(qr_data)
        
        logger.info(f"✅ [start] QR code generated (PNG, base64 encoded, {len(qr_image_data)} chars)")
    except Exception as e:
        logger.error(f"❌ [start] QR generation error: {str(e)}")
        return render(
            request,
            "qr_login/start.html",
            {**base_context, "error": f"QR generation error: {str(e)}"},
            status=500,
        )
    
    logger.info(f"📄 [start] Rendering template with request_id={request_id}")
    logger.info(f"   Supabase URL: {settings.SUPABASE_URL}")
    logger.info(f"   Supabase ANON Key length: {len(settings.SUPABASE_ANON_KEY) if settings.SUPABASE_ANON_KEY else 0}")
    
    # Render template with polling setup
    return render(
        request,
        "qr_login/start.html",
        {
            **base_context,
            "request_id": request_id,
            "token": token,
            "qr_image": qr_image_data,
                "qr_expires_in_seconds": QR_LOGIN_EXPIRES_IN_SECONDS,
                "expires_at": expires_at,
            "supabase_url": settings.SUPABASE_URL,
            "supabase_anon_key": settings.SUPABASE_ANON_KEY,
        },
    )


@require_http_methods(["POST"])
def check_status(request):
    """
    Check if login request was approved.
    Called by browser polling or triggered by Realtime.
    
    Request body: {"request_id": "<uuid>"}
    Response: {"status": "pending|approved|rejected|expired", "user_id": <str|null>, ...}
    """
    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
    except (json.JSONDecodeError, AttributeError):
        logger.error("❌ [check_status] Invalid JSON request")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if not request_id:
        logger.error("❌ [check_status] Missing request_id")
        return JsonResponse({"error": "Missing request_id"}, status=400)
    
    logger.info(f"🔍 [check_status] Polling request: {request_id}")
    
    supabase = get_service()
    
    try:
        login_request = supabase.get_login_request(request_id)
    except Exception as e:
        logger.error(f"❌ [check_status] Database error: {str(e)}")
        return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)
    
    if not login_request:
        logger.error(f"❌ [check_status] Request not found: {request_id}")
        return JsonResponse({"error": "Request not found"}, status=404)
    
    # Check if expired
    expires_at = datetime.fromisoformat(login_request["expires_at"])
    now = timezone.now()
    is_expired = now > expires_at
    
    status = login_request["status"]
    user_id = login_request.get("user_id")
    username = None
    
    # If approved, fetch username from users table
    if status == "approved" and user_id:
        logger.info(f"   👤 Fetching username for user_id: {user_id}")
        try:
            user = supabase.get_user(user_id)
            if user:
                username = user.get("username") or user.get("name")
                logger.info(f"   ✅ Username found: {username}")
            else:
                logger.warning(f"   ⚠️ User not found in database")
        except Exception as user_error:
            logger.warning(f"   ⚠️ Could not fetch user: {str(user_error)}")
    
    logger.info(f"✅ [check_status] Result from Supabase:")
    logger.info(f"   status: {status}")
    logger.info(f"   user_id: {user_id}")
    logger.info(f"   username: {username}")
    logger.info(f"   approved_at: {login_request.get('approved_at')}")
    logger.info(f"   expires_at: {expires_at}")
    logger.info(f"   now: {now}")
    logger.info(f"   expired: {is_expired}")
    logger.info(f"   Full record: {login_request}")
    
    response_data = {
        "status": status,
        "user_id": user_id,
        "username": username,
        "approved_at": login_request.get("approved_at"),
        "expired": is_expired,
    }
    
    logger.info(f"   Sending response: {response_data}")
    
    return JsonResponse(response_data)


@require_http_methods(["POST"])
def complete_login(request):
    """
    Complete the login by creating session.
    Called by browser after detecting approved status.
    
    Request body: {"request_id": "<uuid>"}
    Response: {"success": true, "redirect": "/dashboard/"}
    """
    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
    except (json.JSONDecodeError, AttributeError):
        logger.error("❌ [complete_login] Invalid JSON request")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if not request_id:
        logger.error("❌ [complete_login] Missing request_id")
        return JsonResponse({"error": "Missing request_id"}, status=400)
    
    logger.info(f"🎯 [complete_login] Completing login for request: {request_id}")
    
    supabase = get_service()
    
    try:
        login_request = supabase.get_login_request(request_id)
    except Exception as e:
        logger.error(f"❌ [complete_login] Database error: {str(e)}")
        return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)
    
    if not login_request:
        logger.error(f"❌ [complete_login] Request not found: {request_id}")
        return JsonResponse({"error": "Request not found"}, status=404)
    
    # Verify status is approved
    if login_request["status"] != "approved":
        logger.warning(f"⚠️ [complete_login] Request not approved: status={login_request['status']}")
        return JsonResponse({"error": "Request not approved"}, status=403)
    
    # Verify user_id is set
    user_id = login_request.get("user_id")
    if not user_id:
        logger.error(f"❌ [complete_login] User ID not set in request")
        return JsonResponse({"error": "User ID not set"}, status=403)
    
    # Fetch username for display
    username = None
    supabase = get_service()
    try:
        user = supabase.get_user(user_id)
        if user:
            username = user.get("username") or user.get("name")
            logger.info(f"   👤 Username: {username}")
        else:
            logger.warning(f"   ⚠️ User not found in database")
    except Exception as user_error:
        logger.warning(f"   ⚠️ Could not fetch user: {str(user_error)}")
    
    logger.info(f"   ✅ Status=approved, User ID: {user_id}")
    
    # Verify not expired
    expires_at = datetime.fromisoformat(login_request["expires_at"])
    now = timezone.now()
    if now > expires_at:
        logger.error(f"❌ [complete_login] Request expired: expires_at={expires_at}, now={now}")
        return JsonResponse({"error": "Request expired"}, status=410)
    
    logger.info(f"   ✅ Request not expired")
    
    # Create session
    logger.info(f"📝 [complete_login] Creating Django session...")
    logger.info(f"   Session backend: {request.session.__class__.__module__}.{request.session.__class__.__name__}")
    logger.info(f"   Session key before: {request.session.session_key}")
    logger.info(f"   SESSION_COOKIE_NAME setting: {settings.SESSION_COOKIE_NAME if hasattr(settings, 'SESSION_COOKIE_NAME') else 'NOT SET'}")
    logger.info(f"   Setting session data:")
    
    request.session["supabase_user_id"] = str(user_id)
    request.session["qr_login_request_id"] = request_id
    request.session["supabase_authenticated_at"] = login_request.get("approved_at", now.isoformat())
    request.session.set_expiry(60 * 60 * 8)  # 8 hours
    
    logger.info(f"      - supabase_user_id: {request.session.get('supabase_user_id')}")
    logger.info(f"      - qr_login_request_id: {request.session.get('qr_login_request_id')}")
    logger.info(f"      - supabase_authenticated_at: {request.session.get('supabase_authenticated_at')}")
    logger.info(f"   Full session dict: {dict(request.session)}")
    
    try:
        request.session.save()  # Explicitly save the session
        logger.info(f"✅ [complete_login] Session saved successfully")
        logger.info(f"   Session key after save: {request.session.session_key}")
        logger.info(f"   Session modified: {request.session.modified}")
        logger.info(f"   Session accessed: {request.session.accessed}")
        logger.debug(f"   Full session data after save: {dict(request.session)}")
    except Exception as e:
        logger.error(f"❌ [complete_login] Failed to save session: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return JsonResponse({"error": f"Failed to save session: {str(e)}"}, status=500)
    
    # Prepare response with session cookie info
    response_data = {
        "success": True,
        "redirect": "/",  # Dashboard is at root path
        "username": username,
        "user_id": user_id
    }
    response = JsonResponse(response_data)
    
    logger.info(f"🎉 [complete_login] SUCCESS - Preparing response")
    logger.info(f"   Response status: 200")
    logger.info(f"   Response body: {response_data}")
    logger.info(f"   Response Content-Type: application/json")
    
    # Log cookies that will be sent
    logger.info(f"   Cookies in response:")
    for cookie_name, cookie_val in response.cookies.items():
        logger.info(f"      - {cookie_name}: (value set by Django)")
    
    return response


@require_http_methods(["GET", "POST"])
def logout(request):
    """Logout the user by clearing the session and redirecting to QR login."""
    request.session.flush()
    return redirect("qr_login:start")


@csrf_exempt
@require_http_methods(["POST"])
def approve_from_android(request):
    """Approve a QR login request from the Android app using a Supabase user session."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    token = str(data.get("token", "")).strip()
    request_id = str(data.get("request_id", "")).strip()

    if not token and not request_id:
        return JsonResponse({"success": False, "error": "Missing QR token or request_id"}, status=400)

    for value, label in ((token, "QR token"), (request_id, "request_id")):
        if not value:
            continue
        try:
            uuid.UUID(value)
        except (TypeError, ValueError):
            return JsonResponse({"success": False, "error": f"Invalid {label}"}, status=400)

    supabase = get_service()

    authorization = request.headers.get("Authorization", "")
    user_id = None
    if authorization.startswith("Bearer "):
        access_token = authorization.removeprefix("Bearer ").strip()
        user_id = supabase.get_auth_user_id(access_token)
    else:
        user_id = str(data.get("user_id", "")).strip()

    if not user_id:
        return JsonResponse({"success": False, "error": "Missing authenticated user"}, status=401)

    try:
        uuid.UUID(user_id)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid user_id"}, status=400)

    if not supabase.get_user(user_id):
        return JsonResponse({"success": False, "error": "User not found"}, status=404)

    try:
        approved_at = timezone.now().isoformat()
        if token:
            result = supabase.approve_login_request_by_token(token, user_id, approved_at)
        else:
            result = supabase.update_login_request(
                request_id,
                {
                    "status": "approved",
                    "user_id": user_id,
                    "approved_at": approved_at,
                },
            )
    except Exception as e:
        logger.error(f"❌ [approve_from_android] Failed to approve QR login: {str(e)}")
        return JsonResponse({"success": False, "error": "Failed to approve QR login"}, status=500)

    if not result:
        return JsonResponse({"success": False, "error": "QR code is invalid, expired, or already used"}, status=404)

    return JsonResponse({
        "success": True,
        "status": "approved",
        "request_id": result.get("id"),
        "user_id": user_id,
    })


@require_http_methods(["POST"])
def test_approve(request):
    """
    TEST ENDPOINT: Simulate mobile app approving a login request.
    Usage: curl -X POST http://localhost:8000/qr-login/test-approve/ \
             -H "Content-Type: application/json" \
             -d '{"request_id": "<uuid>", "user_id": "9b79c55b-99b9-4bd0-a592-4a26c216ab8c"}'
    
    This endpoint is for testing the QR login flow without a real mobile app.
    """
    if settings.DEBUG is False:
        return JsonResponse({"error": "Test endpoint only available in DEBUG mode"}, status=403)
    
    try:
        data = json.loads(request.body)
        request_id = data.get("request_id")
        user_id = data.get("user_id")
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    if not request_id or not user_id:
        return JsonResponse({"error": "Missing request_id or user_id"}, status=400)
    
    supabase = get_service()
    
    try:
        # Update login request to approved
        result = supabase.update_login_request(
            request_id,
            {
                "status": "approved",
                "user_id": user_id,
                "approved_at": timezone.now().isoformat(),
            }
        )
        
        return JsonResponse({
            "success": True,
            "message": "Login request approved",
            "data": result,
        })
    except Exception as e:
        return JsonResponse({"error": f"Failed to approve: {str(e)}"}, status=500)