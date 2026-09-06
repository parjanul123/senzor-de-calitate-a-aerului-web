# QR login Supabase

Rularea migrarilor Django creeaza tabela `public.web_login_requests`, triggerul de Supabase Realtime si functia RPC securizata `approve_web_login_request`.

Aplicatia Android trebuie sa trimita tokenul rezultat din scanarea QR catre Supabase, dupa ce utilizatorul este autentificat, folosind:

```kotlin
supabase.postgrest.rpc("approve_web_login_request", mapOf("request_token" to token))
```

Functia seteaza atomic `status = 'approved'`, `user_id = auth.uid()` si `approved_at`. Nu acordati aplicatiei Android acces direct de `UPDATE` la tabela. Tokenul este valid 60 de secunde, iar site-ul il consuma o singura data dupa notificarea Broadcast.

Alternativ, aplicatia Android poate aproba login-ul prin backend-ul web public, trimitand tokenul scanat si access token-ul Supabase al utilizatorului autentificat:

```http
POST /qr-login/approve/
Authorization: Bearer <supabase_access_token>
Content-Type: application/json

{"token":"<tokenul-din-qr>"}
```

Backend-ul valideaza access token-ul in Supabase Auth si aproba request-ul pentru utilizatorul autentificat.

Pentru compatibilitate cu aplicatia Android locala existenta, endpoint-ul accepta si payload-ul vechi cu `request_id` si `user_id`:

```http
POST /qr-login/approve/
Content-Type: application/json

{"request_id":"<request_id_din_web>","user_id":"<uuid_utilizator>"}
```

Formatul recomandat ramane cel cu `Authorization: Bearer <supabase_access_token>` si `token`, pentru ca leaga aprobarea de sesiunea reala Supabase a utilizatorului din Android.