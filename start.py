#!/usr/bin/env python
"""
Auto-setup script for Senzor de Calitate Web
- Verifică conexiunea la Supabase
- Testează INSERT în web_login_requests
- Pornește Django server
"""

import os
import sys
import django
import logging
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Configure logging for detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("  🚀 SENZOR DE CALITATE WEB - AUTO SETUP & START")
print("="*70 + "\n")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.conf import settings
from supabase import create_client
from supabase.lib.client_options import ClientOptions

def identify_key_type(key: str) -> str:
    """Identify if key is ANON or SERVICE_ROLE"""
    if key.startswith("sb_publishable_"):
        return "ANON (public, read-only)"
    elif key.startswith("sb_secret_"):
        return "SERVICE_ROLE (admin, full access)"
    else:
        return "UNKNOWN"

def log_error_details(error: Exception, stage: str):
    """Extract and log complete error details from Supabase response"""
    print(f"\n{'='*70}")
    print(f"❌ ERROR AT STAGE: {stage}")
    print(f"{'='*70}")
    
    # Log the full exception
    logger.exception(f"Full exception traceback:")
    
    # Try to extract Supabase-specific error details
    error_str = str(error)
    error_dict = getattr(error, '__dict__', {})
    
    print(f"\n📋 Error Details:")
    print(f"  Type: {type(error).__name__}")
    print(f"  Message: {error_str}")
    
    # Check if it's a PostgrestException or APIError
    if hasattr(error, 'resp'):
        resp = error.resp
        print(f"\n  Response Status: {getattr(resp, 'status', 'N/A')}")
        print(f"  Response Headers: {getattr(resp, 'headers', {})}")
        
        if hasattr(resp, 'content'):
            try:
                content = json.loads(resp.content) if isinstance(resp.content, str) else resp.content
                print(f"  Response Body:")
                print(f"    {json.dumps(content, indent=6)}")
            except:
                print(f"  Response Body: {resp.content}")
    
    if hasattr(error, 'message'):
        print(f"  Supabase Message: {error.message}")
    
    if hasattr(error, 'code'):
        print(f"  Error Code: {error.code}")
    
    if hasattr(error, 'details'):
        print(f"  Details: {error.details}")
    
    if hasattr(error, 'hint'):
        print(f"  Hint: {error.hint}")
    
    # Check for RLS specifically
    if "row-level security" in error_str.lower() or "rls" in error_str.lower():
        print(f"\n🔒 DIAGNOSIS: Row Level Security (RLS) Policy Blocking")
        print(f"   → RLS is ENABLED on web_login_requests table")
        print(f"   → ANON key cannot bypass RLS policies")
        print(f"\n   FIX: Run in Supabase SQL Editor:")
        print(f"   ALTER TABLE web_login_requests DISABLE ROW LEVEL SECURITY;")
        return "RLS_POLICY"
    
    elif "invalid api key" in error_str.lower():
        print(f"\n🔑 DIAGNOSIS: Invalid or Expired API Key")
        print(f"   → Regenerate ANON key in Supabase Settings")
        return "INVALID_API_KEY"
    
    elif "permission denied" in error_str.lower() or "unauthorized" in error_str.lower():
        print(f"\n⛔ DIAGNOSIS: Permission Denied")
        print(f"   → Check Supabase RLS policies on table")
        return "PERMISSION_DENIED"
    
    elif "not found" in error_str.lower() or "404" in error_str.lower():
        print(f"\n❓ DIAGNOSIS: Table or Resource Not Found")
        print(f"   → Verify web_login_requests table exists")
        return "NOT_FOUND"
    
    else:
        print(f"\n❓ DIAGNOSIS: Unknown Error")
        return "UNKNOWN"

try:
    print("📋 Step 1: Validating Supabase Configuration...")
    print("-" * 70)
    
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_ANON_KEY
    key_type = identify_key_type(key)
    
    print(f"✅ SUPABASE_URL: {url}")
    print(f"✅ SUPABASE_KEY Type: {key_type}")
    print(f"✅ Key Length: {len(key)} chars")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_ANON_KEY not configured in .env")
    
    # Create client
    print("\n📋 Step 2: Creating Supabase Client...")
    print("-" * 70)
    
    client = create_client(url, key)
    print(f"✅ Supabase client initialized")
    
    # Test connection - SELECT
    print("\n📋 Step 3: Testing SELECT query (table existence)...")
    print("-" * 70)
    
    try:
        select_response = client.table("web_login_requests").select("*").limit(1).execute()
        print(f"✅ SELECT works - table 'web_login_requests' exists")
        print(f"   Retrieved {len(select_response.data)} rows")
    except Exception as select_error:
        log_error_details(select_error, "SELECT TEST")
        sys.exit(1)
    
    # Test INSERT (RLS check)
    print("\n📋 Step 4: Testing INSERT query (RLS check)...")
    print("-" * 70)
    
    # Use proper UTC timezone-aware datetime
    test_expires = (datetime.now(timezone.utc) + timedelta(seconds=60)).isoformat()
    test_data = {
        "status": "pending",
        "user_id": None,
        "expires_at": test_expires
    }
    
    print(f"  Attempting INSERT with data:")
    print(f"    {json.dumps(test_data, indent=6, default=str)}")
    print(f"\n  Key Type Used: {key_type}")
    
    try:
        # Call SupabaseService directly to see what it sends
        from config.supabase_client import get_service
        supabase_service = get_service()
        
        print(f"\n  Calling create_login_request()...")
        insert_response = supabase_service.create_login_request(test_expires)
        
        if insert_response and isinstance(insert_response, dict) and insert_response.get('id'):
            test_id = insert_response.get('id')
            test_token = insert_response.get('token')
            print(f"\n✅ INSERT SUCCESSFUL!")
            print(f"   Created record ID: {test_id}")
            print(f"   Token: {test_token}")
            
            # Clean up
            print(f"\n📋 Step 5: Cleaning up test record...")
            print("-" * 70)
            try:
                delete_response = client.table("web_login_requests").delete().eq("id", test_id).execute()
                print(f"✅ Test record deleted")
            except Exception as cleanup_error:
                print(f"⚠️  Warning: Could not delete test record {test_id}")
                logger.warning(f"Cleanup error: {cleanup_error}")
            
            # Success - start server
            print("\n" + "="*70)
            print("  ✅ ALL CHECKS PASSED - STARTING DJANGO SERVER")
            print("="*70 + "\n")
            import subprocess
            subprocess.run([sys.executable, "manage.py", "runserver"])
        else:
            print(f"\n❌ INSERT returned no data")
            print(f"   Response: {insert_response}")
            sys.exit(1)
            
    except Exception as insert_error:
        diagnosis = log_error_details(insert_error, "INSERT TEST")
        
        if diagnosis == "RLS_POLICY":
            print(f"\n🔗 Next Steps:")
            print(f"   1. Go to: https://app.supabase.com/project/eakzxbfcwbgfxfujzote/sql")
            print(f"   2. Run: ALTER TABLE web_login_requests DISABLE ROW LEVEL SECURITY;")
            print(f"   3. Run this script again: python start.py")
        
        sys.exit(1)
    
except ValueError as config_error:
    print(f"\n❌ CONFIGURATION ERROR: {config_error}")
    sys.exit(1)
except Exception as setup_error:
    log_error_details(setup_error, "SETUP")
    sys.exit(1)
