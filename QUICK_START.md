# 🚀 Ghid de Pornire Rapidă

## Configurare Inițială

### 1. Setează Variabilele de Mediu

Copiază `.env.example` în `.env`:

```bash
cp .env.example .env
```

Editează `.env` cu valorile tale Supabase:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### 2. Instalează Dependențele

```bash
pip install -r requirements.txt
```

### 3. Rulează Serverul

```bash
python manage.py runserver
```

Acces: **http://localhost:8000**

## 📱 Fluxul de Utilizare

### 1. **Conectare (QR Login)**
- Accesează `/qr-login/`
- Afișează QR code care expira în 60 de secunde
- App mobile scanează QR și confirmă
- Ești redirecționat automat la Dashboard

### 2. **Dashboard Principal**
- Vizualizează toate dispozitivele tale
- Ultimele măsurători pe fiecare device
- Status (🟢 Online / ⚫ Offline)

### 3. **Dashboard Dispozitiv**
- Clic pe "Vezi Dashboard Detaliat"
- 9 grafice interactive cu Chart.js
- Ultimele valori ale senzorilor
- Sumă cu toți parametrii

### 4. **Istoric Măsurători**
- Tabel complet cu toate măsurătorile
- Filtrare: 100/500/1000 înregistrări
- Toți senzori vizibili

### 5. **Gestionare Dispozitive**
- Lista tuturor dispozitivelor
- Status și ultima sincronizare
- Acces rapid la Dashboard/Istoric

## 🔧 Funcționare Internă

### Autentificare

```
1. User: GET /qr-login/
2. Backend: Generează WebLoginRequest cu UUID token + TTL 60s
3. Frontend: Afișează QR code cu token
4. App Mobile: Scanează QR și aprobă pe Supabase
5. Frontend: Polling la /qr-login/status/ (2s)
6. Detectează status APPROVED
7. POST /qr-login/complete/
8. Django: Stochează supabase_user_id în sesiune
9. User: Redirect la Dashboard
```

### Recuperare Date

```python
# Exemplu din views:
service = get_service()

# Utilizator
user = service.get_user(user_id)

# Dispozitive (filtrare după user)
devices = service.get_user_devices(user_id)

# Măsurători (cu verificare acces)
measurements = service.get_device_measurements(device_id, user_id)
```

### Middleware de Protecție

```python
# config/auth_middleware.py
- Verifica supabase_user_id în sesiune
- Redirect la /qr-login/ dacă nu autentificat
- Exceptie: /qr-login/* paths
```

## 🗄️ Structura Bază de Date

### Relații

```
users
  ↓ (1:N)
devices
  ↓ (1:N)
measurements

web_login_requests → users (QR login)
```

### Filtrare Siguranță

Toată datele sunt filtrate după `supabase_user_id`:

```python
# Doar dispozitivele USER-ului:
devices = supabase.table("devices").select("*").eq("user_id", user_id)

# Doar măsurători din dispozitivele USER-ului:
# (Verifica că device aparține user -> apoi citește măsurători)
```

## 📊 Senzori Disponibili

Pe Dashboard Dispozitiv, grafice pentru:

1. **Temperatură** (°C) - Roșu
2. **Umiditate** (%) - Cyan
3. **Presiune** (hPa) - Gri
4. **CO₂** (ppm) - Portocaliu
5. **PM1.0** (μg/m³) - Albastru
6. **PM2.5** (μg/m³) - Roșu deschis
7. **PM10** (μg/m³) - Orange
8. **Lux** (lumeni) - Galben
9. **VOC** (ppb) - Mov

Fiecare grafic:
- 1000+ puncte de date (configurable)
- Timeline complet
- Tooltip pe hover
- Download/PNG posibil (Chart.js feature)

## ⚠️ Debugging

### "SUPABASE_URL not set"

```bash
# Verifica .env file:
echo $SUPABASE_URL

# Trebui:
SUPABASE_URL=https://your-project.supabase.co
```

### "Device not found"

- Check `/devices/` - sunt dispozitive?
- Verifica în Supabase: `devices.user_id == session['supabase_user_id']`
- Check network tab: ce error returneaza API?

### Nicio Măsurătoare

- Dispozitivul nu a trimis date în Supabase
- Check `measurements` table cu:
  ```sql
  SELECT * FROM measurements 
  WHERE device_id = 'your-device-id' 
  LIMIT 10;
  ```

### Session Expirat

- Logout: `/qr-login/logout/`
- Login din nou: `/qr-login/`
- Session expira după 8 ore inactivitate

## 🚀 Deployment (Railway)

1. Push pe Git
2. Railway conectează automât din `railway.json`
3. Set variables:
   ```
   DJANGO_DEBUG=false
   DJANGO_SETTINGS_MODULE=config.settings.production
   DATABASE_URL=postgresql://...
   SUPABASE_URL=...
   SUPABASE_ANON_KEY=...
   ```
4. Railway rulează:
   ```
   python manage.py migrate
   gunicorn config.wsgi
   ```

## 📚 Fișiere Importante

- `config/supabase_client.py` - Servicul central (singura locație pentru Supabase queries)
- `config/auth_middleware.py` - Protecție sesiune
- `apps/dashboard/services.py` - Business logic dashboard
- `templates/base.html` - Layout principal (Bootstrap 5)
- `IMPLEMENTATION.md` - Documentație tehnică completă

---

**Ai nevoie de ajutor?** Citește `IMPLEMENTATION.md` pentru detalii complete.
