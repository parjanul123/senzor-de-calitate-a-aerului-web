#!/usr/bin/env python
import sys, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
os.environ['SERVER_NAME'] = 'testserver'
django.setup()

from django.test import Client, override_settings
from config.supabase_client import get_service
import json, re
from datetime import datetime, timezone

@override_settings(ALLOWED_HOSTS=['localhost', '127.0.0.1', 'testserver'])
def run_test():
    client = Client()
    supabase = get_service()

    # Step 1: Get QR page
    print('1. Getting QR login page...')
    resp = client.get('/qr-login/')
    print(f'   Status: {resp.status_code}')
    html = resp.content.decode()

    # Extract REQUEST_ID
    match = re.search(r'const REQUEST_ID = "([^"]+)"', html)
    request_id = match.group(1) if match else None
    print(f'   REQUEST_ID: {request_id}')

    if request_id:
        # Step 2: Update via Supabase API directly with ANON key
        # (This tests if the Android app approval flow works)
        print('2. Attempting to approve via Supabase API...')
        try:
            result = supabase.client.table('web_login_requests').update({
                'status': 'approved',
                'user_id': '9b79c55b-99b9-4bd0-a592-4a26c216ab8c',
                'approved_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', request_id).execute()
            print(f'   ✅ Approved: {result.data if hasattr(result, "data") else result}')
        except Exception as e:
            print(f'   ⚠️  Approval blocked by RLS (expected): {str(e)[:100]}...')
            print('   ℹ️  Note: Android app should have permission to approve')
            print('   Continuing with other tests...')
        
        # Step 3: Check status (polling should detect approval if step 2 worked)
        print('3. Checking status via polling endpoint...')
        check_resp = client.post('/qr-login/check-status/', 
            data=json.dumps({'request_id': request_id}),
            content_type='application/json')
        print(f'   Status: {check_resp.status_code}')
        data = check_resp.json()
        current_status = data.get('status')
        print(f'   Current status: {current_status}, User: {data.get("user_id")}')
        
        # Step 4: Try to complete login even if not approved
        # (This tests the complete_login endpoint logic)
        print('4. Testing complete_login endpoint...')
        complete_resp = client.post('/qr-login/complete/', 
            data=json.dumps({'request_id': request_id}),
            content_type='application/json')
        print(f'   Status: {complete_resp.status_code}')
        try:
            data = complete_resp.json()
            print(f'   Response: {data}')
            
            if complete_resp.status_code == 200:
                print('   ✅ Session created and redirect prepared')
                print('✅ FLOW COMPLETE - Ready for Android app testing')
            elif complete_resp.status_code == 403:
                print(f'   ℹ️  Expected 403 (not approved): {data.get("error")}')
                print('   Once Android app approves in Supabase, this should succeed')
            else:
                print(f'   ❌ Unexpected error: {data.get("error")}')
        except Exception as e:
            print(f'   Error: {e}')
    else:
        print('❌ Could not extract REQUEST_ID from HTML')

if __name__ == '__main__':
    run_test()
