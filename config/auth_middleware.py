"""
Authentication middleware to check if user is authenticated via Supabase.
"""

import logging
from django.shortcuts import redirect
from django.urls import reverse

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
        
        # Store in request for easy access
        request.supabase_user_id = supabase_user_id
        
        response = self.get_response(request)
        return response
