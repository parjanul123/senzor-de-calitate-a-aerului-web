#!/usr/bin/env python
"""
Test QR login flow end-to-end.
Simulates:
1. Opening QR login page
2. Approving from mobile
3. Completing login on browser
"""

import os
import sys
import json
import re
import time
import django
from urllib.parse import urljoin

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
sys.path.insert(0, 'd:\\senzor de calitate web')
django.setup()

from django.test import Client
from django.urls import reverse
from django.utils import timezone
from apps.qr_login.models import WebLoginRequest

# Initialize test client
client = Client()

print("=" * 70)
print("🧪 QR LOGIN FLOW TEST")
print("=" * 70)

# Step 1: Access QR login page
print("\n1️⃣ STEP 1: Opening /qr-login/")
print("-" * 70)
response = client.get(reverse('qr_login:start'))
print(f"   Status: {response.status_code}")
print(f"   Content-Type: {response.get('Content-Type')}")

if response.status_code == 200:
    # Extract REQUEST_ID from HTML
    html = response.content.decode()
    match = re.search(r'const REQUEST_ID = "([^"]+)"', html)
    if match:
        request_id = match.group(1)
        print(f"   ✅ REQUEST_ID extracted: {request_id}")
        
        # Get the actual request object from DB
        try:
            qr_request = WebLoginRequest.objects.get(id=request_id)
            print(f"   Token: {qr_request.token}")
            print(f"   Status: {qr_request.status}")
            print(f"   Expires: {qr_request.expires_at}")
        except WebLoginRequest.DoesNotExist:
            print(f"   ❌ REQUEST_ID not found in database!")
            sys.exit(1)
    else:
        print("   ❌ Could not extract REQUEST_ID from HTML")
        sys.exit(1)
else:
    print(f"   ❌ Failed to access QR login page")
    sys.exit(1)

# Step 2: Approve the request (simulate mobile app)
print("\n2️⃣ STEP 2: Approving login request (simulate mobile)")
print("-" * 70)

# Use test endpoint
test_user_id = "9b79c55b-99b9-4bd0-a592-4a26c216ab8c"
approve_data = json.dumps({
    "request_id": request_id,
    "user_id": test_user_id,
})

print(f"   Approving with user_id: {test_user_id}")
response = client.post(
    reverse('qr_login:test_approve'),
    data=approve_data,
    content_type='application/json'
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Verify in database
qr_request.refresh_from_db()
print(f"   ✅ DB Status after approve: {qr_request.status}")
print(f"   ✅ DB User ID: {qr_request.user_id}")
print(f"   ✅ DB Approved At: {qr_request.approved_at}")

# Step 3: Check status (what browser polling does)
print("\n3️⃣ STEP 3: Checking status (browser polling)")
print("-" * 70)

check_data = json.dumps({"request_id": request_id})
response = client.post(
    reverse('qr_login:check_status'),
    data=check_data,
    content_type='application/json'
)
print(f"   Status: {response.status_code}")
status_response = response.json()
print(f"   Response: {json.dumps(status_response, indent=2)}")

if status_response.get('status') != 'approved':
    print(f"   ❌ Status is not 'approved'! Got: {status_response.get('status')}")
else:
    print(f"   ✅ Status is 'approved'")

# Step 4: Complete login (what browser does after detecting approval)
print("\n4️⃣ STEP 4: Completing login")
print("-" * 70)

complete_data = json.dumps({"request_id": request_id})
response = client.post(
    reverse('qr_login:complete'),
    data=complete_data,
    content_type='application/json',
)
print(f"   Status: {response.status_code}")
complete_response = response.json()
print(f"   Response: {json.dumps(complete_response, indent=2)}")

if response.status_code == 200 and complete_response.get('success'):
    print(f"   ✅ Login completed successfully!")
    print(f"   Redirect to: {complete_response.get('redirect')}")
    
    # Check session
    print(f"\n5️⃣ STEP 5: Verifying session")
    print("-" * 70)
    
    # Need to make a new request to check session
    response = client.get(reverse('dashboard:index'))  # Try to access dashboard
    
    if response.status_code == 200:
        print(f"   ✅ Dashboard accessible (session valid)")
    else:
        print(f"   ❌ Dashboard returned {response.status_code}")
        print(f"   Likely redirected to: {response.get('Location')}")
else:
    print(f"   ❌ Login completion failed!")
    if response.status_code != 200:
        print(f"   Error: {complete_response.get('error')}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
