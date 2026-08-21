# ✅ Pre-Testing Checklist

## Inainte de a rula testul, verifica aceasta

### 1. Environment Setup ✓
```bash
cd "d:\senzor de calitate web"
```
- [ ] Directory exists and current
- [ ] Run.ps1 file present (`ls run.ps1`)
- [ ] Python 3.14 installed (`python --version` - should show 3.14.x)

### 2. Dependencies ✓
```bash
python -m pip list | findstr "pillow qrcode supabase"
```
Expected:
- [ ] Pillow >= 12.0
- [ ] qrcode >= 8.0
- [ ] supabase >= 2.0

### 3. Django Database ✓
```bash
python manage.py migrate
```
Expected:
- [ ] No migration errors
- [ ] Django tables created in db.sqlite3

### 4. Static Files ✓
```bash
python manage.py collectstatic --noinput
```
Expected:
- [ ] No errors
- [ ] Files collected to staticfiles/

### 5. Code Compilation ✓
```bash
python -m py_compile apps/qr_login/views.py config/auth_middleware.py apps/dashboard/views.py
```
Expected:
- [ ] No syntax errors
- [ ] Silent completion (no output = success)

### 6. Supabase Connection ✓

Check `.env` or settings files contain:
- [ ] SUPABASE_URL = https://eakzxbfcwbgfxfujzote.supabase.co
- [ ] SUPABASE_ANON_KEY = (long key, 140+ chars)

Test connection:
```bash
python << 'EOF'
from config.supabase_client import get_service
client = get_service()
result = client.table("web_login_requests").select("count").execute()
print(f"✅ Supabase connected! Found {result.data} records")
EOF
```
Expected:
- [ ] Connection successful
- [ ] "Supabase connected!" message

### 7. Android App Preparation (if using real app) ✓
- [ ] Android app installed on phone
- [ ] Android app points to correct server (http://localhost:8000 or IP)
- [ ] Android app can reach server (test: open http://SERVER_IP:8000/qr-login/ on Android)
- [ ] Supabase configuration matches in Android app

### 8. Django Server Ready ✓
```bash
python manage.py runserver 0.0.0.0:8000
```
Expected:
- [ ] No configuration errors
- [ ] "Quit the server with CTRL-BREAK" message
- [ ] No red errors in terminal

### 9. Browser Preparation ✓
- [ ] Open http://localhost:8000/qr-login/ in browser
- [ ] Page loads (see QR code)
- [ ] Page doesn't show error 500
- [ ] Press F12 to open DevTools
- [ ] Go to Console tab
- [ ] See "QR Login Configuration" logs

### 10. Log Viewers Ready ✓
- [ ] Browser DevTools Console visible (F12)
- [ ] Django server terminal visible (watching logs)
- [ ] Can toggle between windows during test
- [ ] Have DIAGNOSTIC_COMPLETE_GUIDE.md open for reference

---

## When to Start Test

✅ All checkboxes above complete? → **Ready to test!**

If any checkbox failed:
1. Fix that specific issue
2. Run the fix command again
3. When it shows ✅ complete, re-check

---

## Test Execution

### Option A: Automated (Recommended)
```bash
# Terminal 1: Start server
.\run.ps1

# Terminal 2: Run test (after server shows "ready")
python test_qr_complete_flow.py
```

### Option B: Manual Browser
```bash
# Terminal 1: Start server  
.\run.ps1

# Browser (after server ready):
# Open: http://localhost:8000/qr-login/ + F12 Console
# Scan QR with Android app
# Watch logs in console and terminal
```

### Option C: Browser Console Test (if test-approve works)
```bash
# Terminal 1: Start server
.\run.ps1

# Browser Console (F12):
# Paste and run:
fetch('/qr-login/test-approve/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken()
  },
  body: JSON.stringify({
    request_id: "YOUR_REQUEST_ID_HERE",
    user_id: '9b79c55b-99b9-4bd0-a592-4a26c216ab8c'
  })
}).then(r => r.json()).then(d => {
  console.log("✅ Approval simulated!");
  console.log(d);
})
```

---

## During Test - Watch For

### ✅ Green Signs (SUCCESS):
- Browser console shows "✅ APPROVAL DETECTED!"
- Django terminal shows "✅ [complete_login] Session saved successfully"
- Browser redirects to /dashboard/
- /dashboard/ loads without 403 error

### ❌ Red Signs (PROBLEM):
- Browser console shows "❌" or "Error"
- Django terminal shows "❌" or "Failed"
- Any HTTP status code other than 200
- Page stuck on /qr-login/ after approval
- Browser back at /qr-login/ after redirect

### 📊 Where to Look:
- Browser console → JavaScript flow
- Django terminal → Backend flow
- Use flowchart from DIAGNOSTIC_COMPLETE_GUIDE.md to navigate

---

## After Test

1. **If SUCCESS (✅):**
   - System working! No more fixes needed
   - User can login with Android + QR code

2. **If FAILURE (❌):**
   - Find exact log message showing error
   - Match to symptom table in DIAGNOSTIC_COMPLETE_GUIDE.md
   - Implement targeted fix based on root cause

3. **If UNCLEAR:**
   - Run test again with more console logging enabled
   - Copy all logs to DIAGNOSTIC_COMPLETE_GUIDE.md for analysis

---

## Success Criteria

Test is SUCCESSFUL when:
1. ✅ GET /qr-login/ returns HTTP 200 with QR
2. ✅ POST /qr-login/check-status/ returns status=pending
3. ✅ Android/test approves in Supabase
4. ✅ Polling detects status=approved
5. ✅ POST /qr-login/complete/ returns HTTP 200
6. ✅ Session cookie set in response
7. ✅ Browser redirects to /dashboard/
8. ✅ GET /dashboard/ returns HTTP 200 (not 403)
9. ✅ Page displays user data (not error)
10. ✅ Session persists (F5 refresh stays logged in)

**All 10 criteria met = 🎉 QR LOGIN WORKING**

