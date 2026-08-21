#!/usr/bin/env python
"""Test Supabase connection"""
import os
from supabase import create_client

# Load environment variables
SUPABASE_URL = "https://eakzxbfcwbgfxfujzote.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_ofI6pPkeb2csAsw_ZqhCng_d3ADhRZU"

print("🔌 Testing Supabase connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_ANON_KEY[:30]}...")

try:
    # Initialize Supabase client
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Client created successfully")
    
    # Test query - fetch from web_login_requests
    response = client.table("web_login_requests").select("*").limit(1).execute()
    print(f"✅ Connected! Table exists with {len(response.data)} rows")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nDid you:")
    print("1. Create the 'web_login_requests' table in Supabase?")
    print("2. Disable RLS on the table?")
    print("3. Use the correct 'anon public' key?")
