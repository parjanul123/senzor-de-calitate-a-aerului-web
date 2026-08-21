# QR Login Debugging Guide - Comprehensive Logging Added

## Summary of Changes

I've added **exhaustive logging** to both JavaScript and Django to help diagnose exactly where the flow breaks when the Android app approves the login.

### Changes Made

#### 1. **JavaScript (start.html) - 6 Key Enhancement Areas**

| Area | What Was Added | Purpose |
|------|-----------------|---------|
| Configuration | Detailed log of REQUEST_ID, SUPABASE_URL, ANON_KEY with length checks | Verify template variables are non-empty |
| checkStatus() | Logs at entry, shows REQUEST_ID, HTTP status, full response JSON, approval detection | See exact polling data |
| completeLogin() | Logs at entry, shows fetch attempt, response status/headers, full JSON, redirect URL | Verify complete_login endpoint works |
| Error Handling | Stack traces on all exceptions | See exact error types |
| Redirect | Logs before and after window.location.href | Verify redirect actually executes |

#### 2. **Django (views.py) - Full Logging Coverage**

| Function | Log Points | Details |
|----------|-----------|---------|
| `start()` | ✅ Entry, REQUEST_ID created, QR generation, template render | Verify QR page generates correctly |
| `check_status()` | ✅ Entry with request_id, status/user_id from DB, expiry check, response JSON | Verify polling gets correct data |
| `complete_login()` | ✅ Entry, DB lookup, status verification, user_id check, session creation, save(), success | Verify session is created and saved |

---

## How to Diagnose - Step-by-Step

### **Step 1: Open Browser Developer Tools**
```
F12 → Console tab
```

### **Step 2: Load QR Page**
```
Navigate to http://localhost:8000/qr-login/
```

**Expected Console Output (First 5 seconds):**
```
=== 🔧 QR Login Configuration ===
REQUEST_ID: [UUID like "550e8400-e29b-41d4-a716-446655440000"]
  - Empty? false
  - Length: 36
SUPABASE_URL: https://eakzxbfcwbgfxfujzote.supabase.co
  - Empty? false
SUPABASE_ANON_KEY: ***set*** (length: 142)
EXPIRES_AT: 2025-01-XX...

🚀 Starting QR login flow...
✅ Starting polling immediately (every 2 seconds)
🔄 Attempting Realtime connection (as secondary mechanism)...
```

**If you see:**
- ❌ `REQUEST_ID: (empty)` → REQUEST_ID not passed to template
- ❌ `SUPABASE_URL: (empty)` → Supabase config issue
- ❌ `SUPABASE_ANON_KEY: (empty)` → ANON_KEY not set

### **Step 3: Scan QR Code with Android App**
```
Open Android app
Scan the QR code shown on the page
Android app should update Supabase record
(User can verify in Supabase console)
```

**Expected Console Output (Every 2 seconds during polling):**
```
🔍 [checkStatus] Polling for approval...
   REQUEST_ID: [your UUID]
📡 [checkStatus] Response status: 200
📦 [checkStatus] Response data: {
  "status": "pending",
  "user_id": null,
  "approved_at": null,
  "expired": false
}
✅ [checkStatus] Success
   Status: pending
   User ID: null
   Expired: false
⏳ [checkStatus] Still waiting for approval...
```

### **Step 4: When Android Approves (Status Should Change)**

**Expected Console Output:**
```
🔍 [checkStatus] Polling for approval...
   REQUEST_ID: [your UUID]
📡 [checkStatus] Response status: 200
📦 [checkStatus] Response data: {
  "status": "approved",
  "user_id": "9b79c55b-99b9-4bd0-a592-4a26c216ab8c",
  "approved_at": "2025-01-XX...",
  "expired": false
}
✅ [checkStatus] Success
   Status: approved
   User ID: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   Expired: false
✅ [checkStatus] APPROVAL DETECTED! Status=approved, User ID: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   → Calling completeLogin()
```

**If you DON'T see "APPROVAL DETECTED" after Android approves:**
- ❌ Polling is not getting the updated status from Supabase
- ❌ Verify in Supabase console that the record WAS updated
- ❌ Check for network errors in Console

### **Step 5: completeLogin Should Execute**

**Expected Console Output:**
```
🎯 [completeLogin] Starting login completion...
   REQUEST_ID: [your UUID]
📤 [completeLogin] Sending POST /qr-login/complete/
📡 [completeLogin] Response status: 200
   Headers: content-type: application/json, ...
📦 [completeLogin] Response body: {
  "success": true,
  "redirect": "/dashboard/"
}
✅ [completeLogin] Success response received
   Success: true
   Redirect: /dashboard/
🎉 [completeLogin] Redirecting to: /dashboard/
   Setting window.location.href = /dashboard/
   Executing redirect now...
   Redirect command executed
```

**If you see an error here:**
- ❌ HTTP 403 "Request not approved" → Server still sees status="pending" (DB sync issue)
- ❌ HTTP 410 "Request expired" → 60 seconds passed
- ❌ HTTP 500 "Failed to save session" → Django session backend problem

### **Step 6: Redirect Should Execute**

**Expected Behavior:**
```
Page should navigate to /dashboard/
Browser should load dashboard page
You should be logged in (session created)
```

**If redirect doesn't happen:**
- ❌ Check if "Redirect command executed" appears in console
- ❌ Check if browser actually navigates (URL bar changes)
- ❌ Try manually navigating to /dashboard/ - if you're already logged in, session was created

---

## Django Server-Side Logs

To see Django logs, run server with debug output:

```bash
python manage.py runserver 2>&1 | tee qr_debug.log
```

**Expected Log Pattern:**

```
📲 [start] QR login page requested
   Creating login request with expiry: 2025-01-XX...
✅ [start] Login request created
   Request ID: [UUID]
   Token (QR data): [UUID]
   Generating QR code with data: [UUID]
✅ [start] QR code generated (PNG, base64 encoded, 4872 chars)

🔍 [check_status] Polling request: [UUID]
✅ [check_status] Result: status=pending, user_id=None, expired=False

🔍 [check_status] Polling request: [UUID]
✅ [check_status] Result: status=approved, user_id=9b79c55b-99b9-4bd0-a592-4a26c216ab8c, expired=False

🎯 [complete_login] Completing login for request: [UUID]
   ✅ Status=approved, User ID: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   ✅ Request not expired
📝 [complete_login] Creating Django session...
✅ [complete_login] Session saved successfully
   Session ID: [django_session_id]
   Session data: supabase_user_id=9b79c55b-99b9-4bd0-a592-4a26c216ab8c
🎉 [complete_login] SUCCESS - Redirecting user
```

---

## Diagnostic Flowchart

```
QR Page Loads?
├─ YES → Template variables logged?
│  ├─ NO → Check settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY
│  ├─ YES → Polling starts?
│     ├─ YES → Android approves, checkStatus detects?
│     │  ├─ NO → Supabase record not updating? Check Android app + RLS
│     │  ├─ YES → completeLogin called?
│     │     ├─ NO → checkStatus not calling completeLogin (status check bug?)
│     │     ├─ YES → POST /complete/ returns 200?
│     │        ├─ NO (403) → Server still sees status=pending (cache/sync bug)
│     │        ├─ NO (500) → Session save failed (backend config)
│     │        ├─ YES → window.location.href executes?
│     │           ├─ NO → JavaScript redirect blocked (browser security?)
│     │           ├─ YES → ✅ LOGIN COMPLETE - Check /dashboard/ loads
│     │  ├─ NO → Realtime/polling not running? Check console for errors
├─ NO → QR page returns HTTP error? Check Django logs
```

---

## Common Issues & Solutions

| Symptom | Root Cause | Solution |
|---------|-----------|----------|
| `checkStatus` never sees "approved" | Android app not updating Supabase OR polling not getting updates | Verify Supabase has approval in console. Check network tab for fetch errors. |
| `complete_login` returns HTTP 403 | Server DB query is stale | Django querying old data? Check if Realtime disabled. Try hard refresh. |
| Session not persisting | `request.session.save()` failed silently | Check Django logs for "Failed to save session". Verify DB connection. |
| Page doesn't redirect after 403 | completeLogin() catches error and shows message | This is correct - approving required before redirect. |
| Redirect URL doesn't change | `window.location.href` blocked or slow browser | Check if URL changes in address bar. Try waiting. Check browser console for CSP errors. |

---

## Testing Without Android App

If you want to test without a real Android app:

**Option 1: Use test_approve endpoint (requires DEBUG=True)**
```bash
curl -X POST http://localhost:8000/qr-login/test-approve/ \
  -H "Content-Type: application/json" \
  -d '{"request_id": "[UUID from page]", "user_id": "9b79c55b-99b9-4bd0-a592-4a26c216ab8c"}'
```

**Option 2: Manually update Supabase**
```sql
UPDATE web_login_requests 
SET status = 'approved', 
    user_id = '9b79c55b-99b9-4bd0-a592-4a26c216ab8c',
    approved_at = NOW()
WHERE id = '[UUID from page]';
```

Then open browser console and wait for polling to detect the change (2-4 seconds).

---

## Quick Summary

| Component | Before | After |
|-----------|--------|-------|
| **JavaScript Logging** | ⚠️ Minimal, hard to debug | ✅ **Exhaustive at every step** |
| **Django Logging** | ❌ None | ✅ **Full trace of execution** |
| **Error Messages** | ⚠️ Generic | ✅ **Specific with context** |
| **Visibility into Data** | ❌ Can't see values | ✅ **All request/response data logged** |

**Next Step:** Follow the diagnostic steps above with browser console open (F12), scan with Android app, and watch console logs to identify exact failure point.

