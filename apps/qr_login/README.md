# QR login Supabase

Rularea migrarilor Django creeaza tabela `public.web_login_requests`, triggerul de Supabase Realtime si functia RPC securizata `approve_web_login_request`.

Aplicatia Android trebuie sa trimita tokenul rezultat din scanarea QR catre Supabase, dupa ce utilizatorul este autentificat, folosind:

```kotlin
supabase.postgrest.rpc("approve_web_login_request", mapOf("request_token" to token))
```

Functia seteaza atomic `status = 'approved'`, `user_id = auth.uid()` si `approved_at`. Nu acordati aplicatiei Android acces direct de `UPDATE` la tabela. Tokenul este valid 60 de secunde, iar site-ul il consuma o singura data dupa notificarea Broadcast.