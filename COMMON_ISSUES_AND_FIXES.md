# 🐛 Common Issues & Quick Fixes

## Problema: Test Script Nu Ruleaza

### Simptomele
```
Traceback (most recent call last):
  File "test_qr_complete_flow.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

### Soluție
```bash
pip install requests
python test_qr_complete_flow.py
```

---

## Problema: Server Nu Se Porneste

### Simptom 1: Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Soluție:**
```bash
# Kill any existing Python processes
Get-Process python | Stop-Process -Force

# Or use different port
python manage.py runserver 8001
```

### Simptom 2: Django Error
```
ModuleNotFoundError: No module named 'django'
```

**Soluție:**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Simptom 3: Database Error
```
django.db.utils.OperationalError: no such table: django_session
```

**Soluție:**
```bash
python manage.py migrate
python manage.py runserver
```

---

## Problema: REQUEST_ID = Empty in Console

### Simptomele
```
REQUEST_ID: (empty)
  - Empty? true
  - Length: 0
```

### Cauze & Soluții

| Cauza | Verifică | Soluție |
|-------|----------|---------|
| Django didn't create REQUEST_ID | Django logs: `[start]` | Check if `start()` endpoint responds with template |
| Template variable not passed | Django logs: `Rendering template` | Verify `request_id=[UUID]` in logs |
| JavaScript parsing error | Browser console | Clear cache (Ctrl+Shift+Delete), F5 refresh |
| Template not reloading | Browser | Hard refresh: Ctrl+F5 |

**Debug Steps:**
```bash
# 1. Check Django logs for [start] entry
# Should see: ✅ [start] Login request created

# 2. Check browser Network tab (F12)
# GET /qr-login/ should return HTML with REQUEST_ID in <script>

# 3. Force cache clear
# F12 → Network tab → Disable cache → F5
```

---

## Problema: Status Nu Se Schimba la "Approved"

### Simptomele
```
⏳ [checkStatus] Status: pending
⏳ [checkStatus] Status: pending
⏳ [checkStatus] Status: pending
[Continues forever...]
```

### Cauze & Soluții

| Cauza | Verifică | Soluție |
|-------|----------|---------|
| Android app didn't approve | Supabase console | Verify record has status='approved' |
| Browser polling not working | Browser console | Look for "polling attempt" messages |
| Supabase RLS blocking reads | Supabase settings | Check if anon user can read web_login_requests |
| Wrong REQUEST_ID being polled | Browser logs | Verify REQUEST_ID matches in Supabase |

**Debug Steps:**
```bash
# 1. Check Supabase directly
# Open: https://supabase.co/dashboard
# Look at web_login_requests table
# Find your REQUEST_ID
# Verify status column

# 2. Check polling in browser
# F12 Console should show: 
# "POST /qr-login/check-status/" every 2 seconds

# 3. Check response status
# F12 Network tab → check-status → Response
# Should show: {"status": "pending/approved", "user_id": "..."}

# 4. If stuck on pending:
# - Did you actually approve in Android? (check Supabase)
# - If using test-approve: run it again
# - Check timestamp: approved_at should be recent
```

**Common Test Case:**
```javascript
// In browser console:
// Check if REQUEST_ID is correct
console.log("REQUEST_ID:", document.querySelector('script').textContent.match(/REQUEST_ID[^"]*"([^"]+)"/)[1])

// Try manual fetch to check-status
fetch('/qr-login/check-status/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
  body: JSON.stringify({request_id: 'YOUR_UUID_HERE'})
}).then(r => r.json()).then(console.log)
```

---

## Problema: HTTP 403 Dupa Android Approval

### Simptomele
```
✅ [checkStatus] APPROVAL DETECTED!
🎯 [completeLogin] Starting...
❌ [completeLogin] Response 403: Request not approved
```

### Cauza
Server queries Supabase again and still sees status="pending"

### Soluții

**Soluție 1: Wait Longer**
- Supabase Realtime has ~1-2 second delay
- Polling waits 2 seconds before retrying
- Sometimes takes 3-4 seconds total
- Just wait and let it retry

**Soluție 2: Use Delay**
- Edit `apps/qr_login/views.py`
- In `complete_login()`, before status check, add:
```python
import time
time.sleep(1)  # Wait 1 second for Supabase sync
# Then check status
```

**Soluție 3: Increase Polling Interval**
- In `start.html`, change:
```javascript
setInterval(checkStatus, 2000)  // Change to 5000 for 5 seconds
```

---

## Problema: HTTP 500 Dupa Android Approval

### Simptomele
```
❌ [completeLogin] Response 500: Failed to save session
```

### Cauze & Soluții

| Cauza | Verifică | Soluție |
|-------|----------|---------|
| Session backend error | Django logs | Check `Session saved successfully` message |
| Database locked | Django logs | Restart server: `Ctrl+C` then `python manage.py runserver` |
| Corrupted session | Browser | Clear cookies and try again |
| Settings misconfigured | settings/base.py | Verify `SESSION_ENGINE` and `SECRET_KEY` |

**Debug Steps:**
```bash
# 1. Check Django logs for exception
# Should see in terminal where error occurred
# Look for: "[complete_login] Failed to save session:"

# 2. Check exception type
# Logs should show: "Exception type: ..."
# Common: DatabaseError, PermissionError, ValueError

# 3. If DatabaseError:
# Restart server: Ctrl+C
# python manage.py migrate --run-syncdb
# python manage.py runserver

# 4. If PermissionError:
# Check file permissions on db.sqlite3:
dir db.sqlite3
```

---

## Problema: Page Redirecționa dar Django Logs Nu Arata Redirect

### Simptomele
```
Browser:
🎉 [completeLogin] Redirecting to: /dashboard/

Django logs:
[No GET /dashboard/ logged]
```

### Cauza
Redirect happened before POST response sent

**Soluție:**
- This is expected behavior (race condition in logging)
- Page should still load /dashboard/
- If page doesn't load, check browser error

---

## Problema: Dashboard Returns 403 After Redirect

### Simptomele
```
Browser:
🎉 [completeLogin] Redirecting to: /dashboard/

Django logs:
❌ [auth_middleware] No supabase_user_id in session! Redirecting to QR login
```

### Cauza
Session not persisted OR session cookie not sent

### Soluții

**Soluție 1: Check Session Save**
- Django logs should show: `✅ [complete_login] Session saved successfully`
- If not, fix the 500 error first (see above)

**Soluție 2: Check Cookies**
- Browser F12 → Application tab → Cookies
- Should see `sessionid` cookie from localhost
- If missing, session save failed

**Soluție 3: Check Cookie Settings**
- In `settings/base.py`, verify:
```python
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"  # OK
SESSION_COOKIE_HTTPONLY = True  # OK (JS can't access, server can)
SESSION_COOKIE_SAMESITE = "Lax"  # OK (allows cross-site with restrictions)
```

**Soluție 4: Manual Test**
```python
# In Python shell:
python manage.py shell

# Then:
from django.contrib.sessions.models import Session
Session.objects.all().count()  # Should see sessions if they're saved

# Exit shell: exit()
```

---

## Problema: Middleware Logs Show Wrong Session Data

### Simptomele
```
🔐 [auth_middleware] Session keys: []
   supabase_user_id from session: None
```

### Cauza
Session empty or not loaded

### Soluții

**Verifică order al middleware-ului:**
```python
# In settings/base.py, MIDDLEWARE must be:
[
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # MUST be here
    ...
    "config.auth_middleware.RequireAuthMiddleware",  # Custom is last
]
```

If wrong, fix order and restart server.

---

## Problema: CSRF Token Not Found

### Simptomele
```
⚠️ [CSRF] csrftoken cookie not found!
   Available cookies: [...]
```

### Cauza
Django didn't set CSRF cookie

### Soluții

**Soluție 1: Add CSRF Token to Template**
- Edit `start.html`
- Add after `<body>`:
```html
{% csrf_token %}
```

**Soluție 2: Ensure CsrfViewMiddleware**
- Check `settings/base.py`:
```python
"django.middleware.csrf.CsrfViewMiddleware",  # Must be present
```

**Soluție 3: Manual Workaround**
```javascript
// If getCsrfToken() returns null, use:
'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || 'none'
```

---

## Problema: All Logs Show But Page Doesn't Load

### Simptomele
```
Browser logs: ✅ All successful
Django logs: ✅ All successful
But page stays on /qr-login/
```

### Cauza
JavaScript redirect blocked (browser security or typo)

### Soluții

**Soluție 1: Check Window Location**
```javascript
// In browser console:
console.log(window.location.href)
console.log(window.location.pathname)
// Should show current URL being set
```

**Soluție 2: Manual Redirect**
```javascript
// Run in console if redirect stuck:
window.location.href = '/dashboard/'
```

**Soluție 3: Check Browser Console Errors**
- F12 → Console tab
- Look for red errors (not just warnings)
- Fix any JavaScript errors

---

## Problema: Test Script Shows Failure

### Simptomele
```
============================================================
STEP 3: Simulate Android Approval (using test-approve endpoint)
============================================================
Status: 404
❌ Test endpoint not found
```

### Cauza
Test endpoint not registered in URLs

### Soluției
- Test endpoint needs to be added to `apps/qr_login/urls.py`
- Or use manual browser test instead
- test-approve is optional, use manual Android app if not available

---

## 🆘 None of These Help?

1. **Save ALL logs:**
   - Browser console: Ctrl+A, Copy, Paste to file
   - Terminal: Screenshot or copy-paste entire output

2. **Verify setup:**
   - Run PRE_TESTING_CHECKLIST.md from top to bottom
   - Make sure all checks pass

3. **Try from scratch:**
   ```bash
   # Clear database
   rm db.sqlite3
   python manage.py migrate
   
   # Restart server
   python manage.py runserver
   
   # Test again
   python test_qr_complete_flow.py
   ```

4. **Check if Supabase is up:**
   - Go to: https://supabase.co/dashboard
   - Verify web_login_requests table exists
   - Verify your records are updating

5. **Consult diagnostic flowchart:**
   - Open DIAGNOSTIC_COMPLETE_GUIDE.md
   - "🔍 Diagnostic Decision Tree" section
   - Follow flowchart with your specific symptoms

