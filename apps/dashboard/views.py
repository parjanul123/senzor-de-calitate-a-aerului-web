"""
Dashboard views.
"""

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
import json

from apps.dashboard.services import get_dashboard_data, get_device_dashboard_data

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def dashboard(request):
    """Main dashboard - shows user's devices and latest measurements."""
    logger.info(f"📊 [dashboard] Request received")
    logger.info(f"   Session ID: {request.session.session_key}")
    
    user_id = request.session.get("supabase_user_id")
    logger.info(f"   User ID from session: {user_id}")
    
    if not user_id:
        logger.warning(f"❌ [dashboard] No user_id in session, redirecting to QR login")
        return redirect("qr_login:start")
    
    logger.info(f"✅ [dashboard] User authenticated: {user_id}")
    
    try:
        data = get_dashboard_data(user_id)
        logger.info(f"   Dashboard data loaded successfully")
        return render(request, "dashboard/index.html", data)
    except Exception as e:
        logger.error(f"❌ [dashboard] Error loading data: {str(e)}")
        return render(
            request,
            "dashboard/index.html",
            {"error": f"Error loading dashboard: {str(e)}", "user": None, "devices": []},
            status=500
        )


@require_http_methods(["GET"])
def device_dashboard(request, device_id):
    """Device-specific dashboard with detailed charts."""
    logger.info(f"📊 [device_dashboard] Request received for device: {device_id}")
    
    user_id = request.session.get("supabase_user_id")
    logger.info(f"   User ID from session: {user_id}")
    
    if not user_id:
        logger.warning(f"❌ [device_dashboard] No user_id in session")
        return redirect("qr_login:start")
    
    logger.info(f"✅ [device_dashboard] User authenticated: {user_id}")
    
    try:
        data = get_device_dashboard_data(device_id, user_id)
        if not data:
            return render(
                request,
                "dashboard/device_detail.html",
                {"error": "Device not found or access denied"},
                status=404
            )
        
        # Convert chart_data to JSON for template
        data["chart_data_json"] = json.dumps(data["chart_data"])
        
        # Add Supabase credentials and user_id for Realtime
        from django.conf import settings
        data["supabase_url"] = settings.SUPABASE_URL
        data["supabase_key"] = settings.SUPABASE_ANON_KEY
        data["user_id"] = user_id
        
        logger.info(f"   Supabase URL: {data['supabase_url']}")
        logger.info(f"   Chart data keys: {list(data.get('chart_data', {}).keys())}")
        
        return render(request, "dashboard/device_detail.html", data)
    except Exception as e:
        logger.error(f"❌ [device_dashboard] Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return render(
            request,
            "dashboard/device_detail.html",
            {"error": f"Error loading device dashboard: {str(e)}"},
            status=500
        )
