#!/usr/bin/env python
"""
Supabase SQL Query Runner - Disable RLS on users table
Run this to disable RLS policies for testing
"""

import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables not set")
    exit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 100)
print("SUPABASE SQL OPERATIONS - DISABLE RLS ON USERS TABLE")
print("=" * 100)

# Note: RLS can only be disabled by a service role, not with ANON key
# This is a limitation, so we'll provide the SQL command to run manually

sql_commands = """
-- Run these commands in Supabase SQL Editor (at https://app.supabase.com)
-- Project: senzor-calitate-web

-- 1. Disable RLS on users table
ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- 2. Verify RLS status
SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'users';

-- 3. Test insert (after RLS is disabled)
INSERT INTO users (id, username) VALUES (
    '3026d270-2ecb-4c61-8724-70573c28be47',
    'SebiTest'
) ON CONFLICT (id) DO UPDATE SET username = 'SebiTest';
"""

print("\n⚠️  NOTE: RLS operations require SERVICE_ROLE key (not available in ANON key)")
print("\n📋 SOLUTION: Run these SQL commands in Supabase SQL Editor:\n")
print(sql_commands)

print("\n" + "=" * 100)
print("INSTRUCTIONS:")
print("=" * 100)
print("""
1. Go to: https://app.supabase.com/project/eakzxbfcwbgfxfujzote/sql/new
2. Copy-paste the SQL commands above
3. Click 'Run' button
4. Return here and run: python insert_test_user.py
""")
print("=" * 100)
