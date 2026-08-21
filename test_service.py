#!/usr/bin/env python
"""Test Supabase service integration in Django"""

import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from config.supabase_client import get_service

print("\n" + "="*60)
print("🧪 TESTING SUPABASE SERVICE IN DJANGO CONTEXT")
print("="*60 + "\n")

try:
    # Get service
    service = get_service()
    print("✅ Service initialized\n")
    
    # Test create login request
    expires_at = (datetime.utcnow() + timedelta(seconds=60)).isoformat()
    print(f"📝 Creating login request (expires_at={expires_at})")
    
    result = service.create_login_request(expires_at)
    if result:
        request_id = result.get('id')
        status = result.get('status')
        print(f"✅ Created: id={request_id}, status={status}\n")
        
        # Test get login request
        print(f"🔍 Fetching login request: {request_id}")
        fetched = service.get_login_request(request_id)
        if fetched:
            print(f"✅ Fetched: status={fetched.get('status')}\n")
            
            # Test update
            print(f"🔄 Updating status to 'approved'")
            updated = service.update_login_request(
                request_id,
                {"status": "approved", "user_id": "12345678-1234-1234-1234-123456789012"}
            )
            if updated:
                print(f"✅ Updated: status={updated.get('status')}")
        else:
            print("❌ Failed to fetch login request")
    else:
        print("❌ Failed to create login request")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
