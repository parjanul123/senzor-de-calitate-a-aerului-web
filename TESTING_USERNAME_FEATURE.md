# Testing Guide: Username Display Feature

## Setup
1. Ensure Django server is running:
   ```bash
   python manage.py runserver
   ```

2. Open QR login page:
   ```
   http://localhost:8000/qr-login/
   ```

## Testing Steps

### Scenario 1: Pending Request (Before Approval)
1. Load QR login page
2. Open browser DevTools → Console tab
3. Look for logs like:
   ```
   ✅ [checkStatus] Status: pending
   ✅ [checkStatus] Username: null
   ```
4. No dialog should appear yet

### Scenario 2: Approval Detected (Main Test)
1. Load QR login page
2. Open DevTools → Console tab
3. Use Android app to approve the request
4. In Console, you should see:
   ```
   ✅ [checkStatus] APPROVAL DETECTED! Status=approved
   ✅ [checkStatus] Username: [USERNAME_FROM_ANDROID_USER]
   🔔 [showApprovalDialog] Showing dialog for username: [USERNAME]
   ```
5. Dialog should appear with message:
   ```
   ✅ Aprobare primită
   
   Vrei să te conectezi la profilul:
   [USERNAME]
   
   [Anulare] [De acord]
   ```

### Scenario 3: User Confirms Login
1. In the dialog, click **"De acord"** button
2. In Console, you should see:
   ```
   ✅ [showApprovalDialog] User confirmed, proceeding with login
   🎯 [completeLogin] Starting login completion...
   📤 [completeLogin] Sending POST /qr-login/complete/
   ✅ [completeLogin] Login successful!
   🔄 [completeLogin] Redirecting to: /dashboard/
   ```
3. Browser should redirect to `/dashboard/`
4. Session should be created (check Django admin or session storage)

### Scenario 4: User Cancels Login
1. In the dialog, click **"Anulare"** button
2. In Console, you should see:
   ```
   ❌ [showApprovalDialog] User declined
   ```
3. Dialog should close
4. Message should appear: "❌ Conectare anulată."
5. Polling should resume (waiting for another approval)

## Debugging Checklist

### If dialog doesn't appear:
- [ ] Check if `status === "approved"` in console logs
- [ ] Check if `username` field is in response from `check_status/`
- [ ] Open DevTools Network tab, check `/qr-login/check-status/` response
- [ ] Look for JavaScript errors in Console

### If username is missing:
- [ ] Check if Android user has `username` field in Supabase `users` table
- [ ] Verify the `user_id` in web_login_requests matches a record in `users`
- [ ] Check Django logs: look for "Fetching username for user_id" messages
- [ ] If not found, backend fallback displays "Necunoscut"

### If modal doesn't display correctly:
- [ ] Check if Bootstrap CSS is loaded (Network tab, look for bootstrap CSS)
- [ ] Check if Bootstrap JS is loaded (should see bundle.min.js)
- [ ] Check Console for any JavaScript errors
- [ ] Test in Chrome/Firefox (not IE - old browser won't work)

## Expected Console Output

### Complete Successful Flow:
```
🎯 [start] QR Login page loaded
📝 Polling started immediately, checking every 2 seconds

🔍 [checkStatus] Polling request: 37a99ba1-8605-4c9a-8a71-45a9c1272d7a
📦 [checkStatus] Response data: {
  "status": "pending",
  "user_id": null,
  "username": null,
  ...
}
⏳ [checkStatus] Still waiting for approval...

[After 30-60 seconds, Android app approves...]

🔍 [checkStatus] Polling request: 37a99ba1-8605-4c9a-8a71-45a9c1272d7a
📦 [checkStatus] Response data: {
  "status": "approved",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "sebi",
  ...
}
✅ [checkStatus] APPROVAL DETECTED!
👤 [check_status] Username: sebi
🔔 [showApprovalDialog] Showing dialog for username: sebi

[User clicks "De acord"]

✅ [showApprovalDialog] User confirmed
🎯 [completeLogin] Starting login completion...
📤 [completeLogin] Sending POST /qr-login/complete/
📡 [completeLogin] Response status: 200
🎉 [completeLogin] Login successful!
🔄 [completeLogin] Redirecting to: /dashboard/
```

## Backend Logs to Check

In Django logs (at DEBUG level), look for:

```
🔍 [check_status] Polling request: <REQUEST_ID>
✅ [check_status] Result from Supabase:
   status: approved
   user_id: 550e8400-e29b-41d4-a716-446655440000
   username: sebi
   approved_at: 2025-01-10T14:30:45.123Z
   expires_at: 2025-01-10T14:35:45.123Z
   now: 2025-01-10T14:33:00.000Z
   expired: false
   Full record: {...}
```

## Troubleshooting Commands

### Check if server is accepting requests:
```bash
curl -X GET http://localhost:8000/qr-login/
```

### Manually test check-status endpoint:
```bash
curl -X POST http://localhost:8000/qr-login/check-status/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <CSRF_TOKEN>" \
  -d '{"request_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

### Check Supabase records directly:
```sql
-- Check pending requests
SELECT id, status, user_id, created_at FROM web_login_requests 
WHERE status = 'pending' LIMIT 5;

-- Check approved requests  
SELECT id, status, user_id, approved_at FROM web_login_requests 
WHERE status = 'approved' LIMIT 5;

-- Check user data
SELECT id, username, name, email FROM users LIMIT 10;
```

## Expected Behavior Summary

| Step | Component | Expected Output |
|------|-----------|-----------------|
| 1 | Page Load | QR code displays, polling starts |
| 2 | Check Status (pending) | `status: "pending"`, no username, no dialog |
| 3 | Android Approves | Supabase updates record |
| 4 | Check Status (approved) | `status: "approved"`, username included |
| 5 | Show Dialog | Bootstrap modal with username appears |
| 6 | User Confirms | User clicks "De acord" |
| 7 | Complete Login | Session created, redirect to dashboard |
| 8 | Dashboard | User logged in and authenticated |

---

## Success Criteria ✅

- [x] Dialog appears with correct username
- [x] "De acord" button completes login
- [x] "Anulare" button cancels and resumes polling
- [x] Username is fetched from Supabase users table
- [x] Session is properly created
- [x] Redirect to /dashboard/ works
- [x] Logging shows all steps clearly
- [x] Modal styling is correct (Bootstrap 5)
