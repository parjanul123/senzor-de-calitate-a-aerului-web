# 🔍 QR Login Debugging - Diagnostic Complete 

## Schimbări Adăugate

### 1. **Logging în Django Views** (`apps/qr_login/views.py`)
- ✅ `start()` - logs QR page creation, request ID, token, QR generation
- ✅ `check_status()` - logs detailed Supabase query results, status, user_id
- ✅ `complete_login()` - logs session creation, data, save(), response

### 2. **Logging în Middleware** (`config/auth_middleware.py`)
- ✅ Logs session ID, session keys
- ✅ Logs if path requires auth
- ✅ Logs if user_id found in session
- ✅ Logs authentication success/failure

### 3. **Logging Configurare** (`config/settings/base.py`)
- ✅ Configurare pentru `apps.qr_login.views` (DEBUG level)
- ✅ Configurare pentru `config.auth_middleware` (DEBUG level)

### 4. **JavaScript Logging Îmbunătățit** (`templates/qr_login/start.html`)
- ✅ Verificări detaliate ale approval condition
- ✅ Logging cookies înainte de redirect
- ✅ Logging detaliat al redirect execution

### 5. **Script de Test** (`test_qr_complete_flow.py`)
- ✅ Testează flux complet: QR load → status check → approval → complete → session

---

## 🚀 Cum Să Testezi

### **Metoda 1: Test Automat cu Script (Recomandare)**

**Dacă test endpoint funcționează:**

```bash
# Terminal 1: Start server
cd "d:\senzor de calitate web"
.\run.ps1

# Terminal 2: Run test script (after server starts)
cd "d:\senzor de calitate web"
python test_qr_complete_flow.py
```

**Output Așteptat:**
```
============================================================
  STEP 1: Load QR Login Page (GET /qr-login/)
============================================================
Status: 200
✅ Extracted REQUEST_ID: [UUID]

============================================================
  STEP 2: Check Initial Status
============================================================
Status: 200
✅ Initial status: pending

============================================================
  STEP 3: Simulate Android Approval (using test-approve endpoint)
============================================================
Status: 200
✅ Approval simulated

============================================================
  STEP 4: Check Updated Status
============================================================
Status: 200
✅ Updated status: approved
   User ID: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
✅ Status is APPROVED and user_id is set!

============================================================
  STEP 5: Complete Login (POST /complete/ - Creates Session)
============================================================
Status: 200
✅ Login completed!
   Redirect: /dashboard/

============================================================
  STEP 6: Verify Session
============================================================
Status: 200
✅ Successfully accessed /dashboard/ - Session is valid!
```

---

### **Metoda 2: Test Manual cu Browser (Pentru Android App Reală)**

#### **Pasul 1: Pornește Serverul**
```bash
cd "d:\senzor de calitate web"
.\run.ps1
# Output: "Starting server at http://localhost:8000/"
```

#### **Pasul 2: Deschide Browser DevTools**
```
http://localhost:8000/qr-login/
Apasă: F12 → Console tab → Setează level la "Verbose"
```

#### **Pasul 3: Observă Logurile Inițiale**
```
=== 🔧 QR Login Configuration ===
REQUEST_ID: [UUID - ar trebui sa fie plin]
  - Empty? false
  - Length: 36
SUPABASE_URL: https://eakzxbfcwbgfxfujzote.supabase.co
  - Empty? false
SUPABASE_ANON_KEY: ***set*** (length: 142)

🚀 Starting QR login flow...
✅ Starting polling immediately (every 2 seconds)
```

**Dacă REQUEST_ID este empty:**
```
❌ PROBLEM: Template variables not populated
→ Check Django logs for errors in start()
```

#### **Pasul 4: Scaneaza QR cu Android App**

**Observă logurile polling (fiecare 2 secunde):**
```
🔍 [checkStatus] Polling for approval...
   REQUEST_ID: [UUID]
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

#### **Pasul 5: Când Android Aprobă**

**Observă în console (1-2 secunde după Android approval):**
```
🔍 [checkStatus] Polling for approval...
   REQUEST_ID: [UUID]
📡 [checkStatus] Response status: 200
📦 [checkStatus] Response data: {
  "status": "approved",
  "user_id": "9b79c55b-99b9-4bd0-a592-4a26c216ab8c",
  "approved_at": "2026-08-06T14:30:45...",
  "expired": false
}
✅ [checkStatus] Success
   Status: approved
   User ID: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   Expired: false
✅ [checkStatus] APPROVAL DETECTED! Status=approved, User ID: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   Type of data.status: string
   data.status === 'approved': true
   data.user_id: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   data.user_id truthy: true
   → Calling completeLogin()
```

**Dacă NU apare "APPROVAL DETECTED" (chiar după Android approval):**
```
⚠️ PROBLEM: Browser polling not detecting approval
→ Verifică in Supabase direct daca record-ul s-a actualizat
→ Check Django logs in terminal: "✅ [check_status] Result from Supabase: status=approved"
```

#### **Pasul 6: completeLogin Se Execută**

**Observă în console:**
```
🎯 [completeLogin] Starting login completion...
   REQUEST_ID: [UUID]
📤 [completeLogin] Sending POST /qr-login/complete/
📡 [completeLogin] Response status: 200
   Headers: content-type: application/json, set-cookie: sessionid=..., ...
📦 [completeLogin] Response body: {
  "success": true,
  "redirect": "/dashboard/"
}
✅ [completeLogin] Success response received
   Success: true
   Redirect: /dashboard/
🎉 [completeLogin] Redirecting to: /dashboard/
   Setting window.location.href = /dashboard/
   Checking cookies before redirect...
   document.cookie = [sesionid cookie ar trebui sa fie aici]
   [TIMEOUT CALLBACK] Executing redirect now...
   [AFTER REDIRECT] This line may not execute if redirect works
```

**Dacă NU apare response success=true:**
- HTTP 403: Server still sees status="pending" (Supabase sync delay?)
- HTTP 500: Session save failed (Django backend issue?)
- HTTP 404: Request not found (database issue?)

---

## 📋 Logurile Django (Server Terminal)

**Observă output-ul din terminal unde ruleaza serverul:**

### **Inițializare:**
```
📲 [start] QR login page requested
   Creating login request with expiry: 2026-08-06T14:31:45.123456+00:00
✅ [start] Login request created
   Request ID: [UUID]
   Token (QR data): [TOKEN-UUID]
   Generating QR code with data: [TOKEN-UUID]
✅ [start] QR code generated (PNG, base64 encoded, 4872 chars)
📄 [start] Rendering template with request_id=[UUID]
   Supabase URL: https://eakzxbfcwbgfxfujzote.supabase.co
   Supabase ANON Key length: 142
```

### **Polling (fiecare 2 secunde):**
```
🔍 [check_status] Polling request: [UUID]
✅ [check_status] Result from Supabase:
   status: pending
   user_id: None
   approved_at: None
   expires_at: 2026-08-06T14:31:45.123456+00:00
   now: 2026-08-06T14:30:50.123456+00:00
   expired: False
   Full record: {'id': '[UUID]', 'token': '[TOKEN]', 'status': 'pending', 'user_id': None, ...}
   Sending response: {'status': 'pending', 'user_id': None, 'approved_at': None, 'expired': False}
```

### **După Android Approval (Status Change):**
```
🔍 [check_status] Polling request: [UUID]
✅ [check_status] Result from Supabase:
   status: approved
   user_id: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   approved_at: 2026-08-06T14:30:55.123456+00:00
   expires_at: 2026-08-06T14:31:45.123456+00:00
   now: 2026-08-06T14:30:56.123456+00:00
   expired: False
   Full record: {'id': '[UUID]', 'token': '[TOKEN]', 'status': 'approved', 'user_id': '9b79c55b-...', ...}
   Sending response: {'status': 'approved', 'user_id': '9b79c55b-99b9-4bd0-a592-4a26c216ab8c', ...}
```

### **Complete Login (Session Creation):**
```
🎯 [complete_login] Completing login for request: [UUID]
   Session backend: django.contrib.sessions.backends.db.SessionStore
   Session key before: None
   Setting session data:
      - supabase_user_id: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
      - qr_login_request_id: [UUID]
      - supabase_authenticated_at: 2026-08-06T14:30:55.123456+00:00
   Full session dict: {'supabase_user_id': '9b79c55b-...', 'qr_login_request_id': '[UUID]', 'supabase_authenticated_at': '...'}
   ✅ Status=approved, User ID: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
   ✅ Request not expired
📝 [complete_login] Creating Django session...
   Session backend: django.contrib.sessions.backends.db.SessionStore
   Session key before: None
   Setting session data:
      - supabase_user_id: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
      - qr_login_request_id: [UUID]
      - supabase_authenticated_at: 2026-08-06T14:30:55.123456+00:00
   Full session dict: {'supabase_user_id': '9b79c55b-99b9-4bd0-a592-4a26c216ab8c', ...}
✅ [complete_login] Session saved successfully
   Session key after save: [sessionid-uuid-long]
   Session modified: False
   Session accessed: True
   Session empty: False
   Full session data after save: {'supabase_user_id': '9b79c55b-...', ...}
🎉 [complete_login] SUCCESS - Preparing response
   Response status: 200
   Response body: {'success': True, 'redirect': '/dashboard/'}
   Response headers will include: Set-Cookie (session)
```

### **Middleware Check (Redirect to Dashboard):**
```
🔐 [auth_middleware] Request: GET /dashboard/
   Session ID: [sessionid-uuid]
   Session keys: ['supabase_user_id', 'qr_login_request_id', 'supabase_authenticated_at']
   supabase_user_id from session: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
✅ [auth_middleware] User authenticated: 9b79c55b-99b9-4bd0-a592-4a26c216ab8c
```

---

## 🚨 Diagnostic Flowchart

```
┌─ Browser deschis pe /qr-login/
│
├─ REQUEST_ID în console = empty?
│  ├─ YES → ❌ Django nu transmite REQUEST_ID
│  │  └─ Check Django logs: "🎯 [start] Rendering template"
│  │     ar trebui sa arate: request_id=[UUID]
│  │
│  └─ NO → ✅ Template variables OK
│
├─ Android scaneaza QR
│
├─ "APPROVAL DETECTED" apare in console?
│  ├─ NO → ❌ Status ramas "pending" (1-3 secunde dupa Android action)
│  │  └─ Check Supabase: record-ul s-a actualizat?
│  │  └─ Check Django logs: "status: pending" sau "status: approved"?
│  │
│  └─ YES → ✅ Status change detected
│
├─ completeLogin() apare in console?
│  ├─ NO → ❌ Approval condition failed
│  │  └─ Check console: Type of data.status, data.user_id truthy?
│  │
│  └─ YES → ✅ completeLogin initiated
│
├─ Response 200 cu success=true?
│  ├─ NO (403) → ❌ Server sees status="pending" still
│  │  └─ Timing issue? Delay intre Supabase update si server check?
│  │
│  ├─ NO (500) → ❌ Session save failed
│  │  └─ Check Django logs: "Failed to save session: [error]"
│  │
│  └─ YES → ✅ Session created
│
├─ window.location.href executa?
│  ├─ NO → ❌ Redirect blocked (browser security?)
│  │  └─ Check browser console para "Redirect command executed"
│  │
│  └─ YES → ✅ Browser navigates to /dashboard/
│
└─ /dashboard/ se incarca?
   ├─ NO (403) → ❌ Middleware vede session fara supabase_user_id
   │  └─ Check Django logs: "Session keys: [...]" ar trebui sa arate supabase_user_id
   │
   └─ YES → ✅ ✅ ✅ SUCCESS - User logged in!
```

---

## 🔧 Debugging: Unde Sa Cauti Probleme

| Simptom | Unde sa cauti | Ce sa verifici |
|---------|--|--|
| REQUEST_ID = empty in console | Django logs | `[start] Rendering template` - ar trebui request_id=[UUID] |
| Status nu se schimba la approved dupa Android | Supabase + Django logs | Ar trebui sa apara "status: approved" in logs |
| HTTP 403 dupa completeLogin | Django logs | `[complete_login] Request not approved: status=pending` - timing issue |
| HTTP 500 dupa completeLogin | Django logs | `[complete_login] Failed to save session: [error]` - backend issue |
| Pagina nu redirecționează | Browser console | Ar trebui "Redirect command executed" |
| /dashboard/ redirecteaza back la QR login | Django logs + middleware | Middleware nu vede supabase_user_id in session |

---

## ✅ Pasul Urmator

1. **Porneste server** cu `.\run.ps1`
2. **Incepe test**:
   - Automat: `python test_qr_complete_flow.py`
   - Manual: Deschide http://localhost:8000/qr-login/ + F12
3. **Scaneaza QR** cu Android app (sau ruleaza test script)
4. **Observa logurile** in browser console + terminal
5. **Identifica exact** unde se opreste fluxul
6. **Raporteaza** log lines care arata problema

Logging-ul este acum suficient de detaliat ca sa raspunda la ORICE intrebare despre fluxul de autentificare.

