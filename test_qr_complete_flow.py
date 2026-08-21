#!/usr/bin/env python
"""
Test script pentru QR Login flow cu logging detaliat.
Testează: 1. GET /qr-login/ 2. Simulare Android approval 3. POST /check-status/ 4. POST /complete/
"""

import json
import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
QR_LOGIN_URL = f"{BASE_URL}/qr-login/"
CHECK_STATUS_URL = f"{BASE_URL}/qr-login/check-status/"
COMPLETE_URL = f"{BASE_URL}/qr-login/complete/"
TEST_APPROVE_URL = f"{BASE_URL}/qr-login/test-approve/"

def get_csrf_token(session):
    """Extract CSRF token from cookies."""
    return session.cookies.get('csrftoken', '')

def print_section(title):
    """Print section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_response(response):
    """Print response details."""
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Body: {response.text}")

# Step 1: Load QR page
print_section("STEP 1: Load QR Login Page (GET /qr-login/)")

session = requests.Session()
response = session.get(QR_LOGIN_URL)
print(f"GET {QR_LOGIN_URL}")
print_response(response)

if response.status_code != 200:
    print("❌ Failed to load QR page!")
    exit(1)

# Extract request_id from HTML
html = response.text
import re
request_id_match = re.search(r'const REQUEST_ID = "([^"]+)"', html)
if not request_id_match:
    print("❌ Could not find REQUEST_ID in HTML!")
    exit(1)

request_id = request_id_match.group(1).strip()
print(f"✅ Extracted REQUEST_ID: {request_id}")

# Get CSRF token
csrf_token = get_csrf_token(session)
print(f"✅ CSRF Token: {csrf_token[:20]}..." if csrf_token else "⚠️ No CSRF token")

# Step 2: Check initial status
print_section("STEP 2: Check Initial Status (POST /check-status/)")

print(f"POST {CHECK_STATUS_URL}")
print(f"Body: {json.dumps({'request_id': request_id}, indent=2)}")

response = session.post(
    CHECK_STATUS_URL,
    json={"request_id": request_id},
    headers={"X-CSRFToken": csrf_token}
)
print_response(response)

if response.status_code != 200:
    print("❌ Failed to check status!")
    exit(1)

initial_status = response.json()
print(f"✅ Initial status: {initial_status['status']}")
print(f"   User ID: {initial_status.get('user_id')}")

# Step 3: Simulate Android approval
print_section("STEP 3: Simulate Android Approval (using test-approve endpoint)")

# For this we need to make a direct POST with user_id
# We'll use a dummy user_id
test_user_id = "9b79c55b-99b9-4bd0-a592-4a26c216ab8c"

print(f"POST {TEST_APPROVE_URL}")
print(f"Body: {json.dumps({'request_id': request_id, 'user_id': test_user_id}, indent=2)}")

response = session.post(
    TEST_APPROVE_URL,
    json={"request_id": request_id, "user_id": test_user_id},
    headers={"X-CSRFToken": csrf_token}
)
print_response(response)

if response.status_code != 200:
    print("⚠️ Test approve endpoint not available or failed")
    print("   (This is OK - Android app would do this in real scenario)")
    print("   Skipping to step 4...")
else:
    print(f"✅ Approval simulated")

# Step 4: Check updated status
print_section("STEP 4: Check Updated Status (POST /check-status/ after approval)")

time.sleep(1)  # Give server time to process

print(f"POST {CHECK_STATUS_URL}")
response = session.post(
    CHECK_STATUS_URL,
    json={"request_id": request_id},
    headers={"X-CSRFToken": csrf_token}
)
print_response(response)

if response.status_code != 200:
    print("❌ Failed to check status!")
    exit(1)

updated_status = response.json()
print(f"✅ Updated status: {updated_status['status']}")
print(f"   User ID: {updated_status.get('user_id')}")

if updated_status['status'] == 'approved' and updated_status.get('user_id'):
    print("✅ Status is APPROVED and user_id is set!")
else:
    print(f"⚠️ Status is not approved yet: {updated_status}")

# Step 5: Complete login (create session)
print_section("STEP 5: Complete Login (POST /complete/ - Creates Session)")

print(f"POST {COMPLETE_URL}")
print(f"Body: {json.dumps({'request_id': request_id}, indent=2)}")
print(f"Cookies before: {session.cookies}")

response = session.post(
    COMPLETE_URL,
    json={"request_id": request_id},
    headers={"X-CSRFToken": csrf_token}
)
print_response(response)

print(f"\nCookies after: {session.cookies}")
print(f"Session cookie: {session.cookies.get('sessionid', 'NOT SET')}")

if response.status_code != 200:
    print(f"❌ Failed to complete login! Status: {response.status_code}")
    if response.status_code == 403:
        print("   Error: Request not approved (DB not synced or status check failed)")
    elif response.status_code == 500:
        print("   Error: Server error (check Django logs)")
    exit(1)

response_data = response.json()
if not response_data.get('success'):
    print(f"❌ Login not successful: {response_data}")
    exit(1)

print(f"✅ Login completed!")
print(f"   Redirect: {response_data.get('redirect')}")

# Step 6: Verify session
print_section("STEP 6: Verify Session (GET /dashboard/)")

print(f"GET {BASE_URL}/dashboard/")
response = session.get(f"{BASE_URL}/dashboard/")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✅ Successfully accessed /dashboard/ - Session is valid!")
elif response.status_code == 302:
    print(f"⚠️ Redirect to: {response.headers.get('Location')}")
    print("   Session might not be recognized")
elif response.status_code == 403:
    print("❌ Access denied to /dashboard/ - Session not created or invalid")
else:
    print(f"❌ Unexpected status: {response.status_code}")

print_section("SUMMARY")
print("✅ Test completed!")
print(f"   REQUEST_ID: {request_id}")
print(f"   Session Cookie: {session.cookies.get('sessionid', 'NOT SET')}")
