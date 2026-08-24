"""
Authentication middleware to check if user is authenticated via Supabase.
"""

import logging
from django.shortcuts import redirect

from config.supabase_client import get_service

logger = logging.getLogger(__name__)


class RequireAuthMiddleware:
    """
    Middleware to check if user has valid Supabase session.
    Redirects to QR login if not authenticated.
    """
    
    # Paths that don't require authentication
    EXEMPT_PATHS = {
        '/qr-login/',
        '/ai/',  # Allow AI interface without authentication for testing
        '/static/',
        '/staticfiles/',
    }

    USERNAME_SETUP_EXEMPT_PATHS = {
        '/profile/',
        '/profile/api/username/',
        '/qr-login/',
        '/qr-login/logout/',
        '/ai/',
        '/static/',
        '/staticfiles/',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        logger.debug(f"🔐 [auth_middleware] Request: {request.method} {request.path}")
        logger.debug(f"   Session ID (sessionid cookie): {request.session.session_key}")
        logger.debug(f"   Session keys: {list(request.session.keys())}")
        logger.debug(f"   Incoming cookies: {dict(request.COOKIES)}")
        
        # Check if path is exempt
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            logger.debug(f"   Path is exempt from auth")
            return self.get_response(request)
        
        # Check if user is authenticated
        supabase_user_id = request.session.get("supabase_user_id")
        logger.debug(f"   supabase_user_id from session: {supabase_user_id}")
        logger.debug(f"   Full session data: {dict(request.session)}")
        
        if not supabase_user_id:
            logger.warning(f"❌ [auth_middleware] No supabase_user_id in session! Redirecting to QR login")
            logger.warning(f"   Session is empty or doesn't contain supabase_user_id")
            logger.warning(f"   This means complete_login() didn't create session OR cookie not sent back")
            return redirect("qr_login:start")
        
        logger.info(f"✅ [auth_middleware] User authenticated: {supabase_user_id}")

        # Force onboarding: user must set username before using other app areas.
        checked_for = request.session.get("username_checked_for")
        username_set = request.session.get("username_set")
        if checked_for != supabase_user_id:
            username_set = None

        if username_set is None:
            try:
                username = get_service().get_username(supabase_user_id)
                username_set = bool(isinstance(username, str) and username.strip())
            except Exception:
                username_set = False
            request.session["username_set"] = username_set
            request.session["username_checked_for"] = supabase_user_id

        if (
            not username_set
            and not any(request.path.startswith(path) for path in self.USERNAME_SETUP_EXEMPT_PATHS)
        ):
            logger.info("🔁 [auth_middleware] Username missing; redirecting user to profile setup")
            return redirect("accounts:profile")
        
        # Store in request for easy access
        request.supabase_user_id = supabase_user_id
        
        response = self.get_response(request)
        return response
