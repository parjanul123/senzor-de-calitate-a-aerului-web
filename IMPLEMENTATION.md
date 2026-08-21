# Implementare Django 5 + Bootstrap 5 + Supabase

Website-ul este complet construit cu:
- **Django 5.0** - Framework web Python
- **Bootstrap 5** - UI framework responsive
- **Supabase (supabase-py client)** - Bază de date PostgreSQL + Auth
- **Chart.js** - Grafice interactive pentru dashboards

## 📋 Structura Aplicației

### Arhitectură

```
Django Web App
├── Autentificare (QR Code Login)
│   └── SessionStorage: supabase_user_id
├── Dashboard
│   ├── Afișare toate dispozitivele
│   ├── Ultima măsurătoare per dispozitiv
│   └── Acces la dashboard detaliat
├── Dispozitive (Gestionare)
│   ├── Listă de dispozitive
│   ├── Status (Online/Offline)
│   └── Ultima sincronizare
├── Măsurători
│   ├── Istoric complet măsurători
│   ├── Filtrare și limitare date
│   └── Export date
└── Dashboard Dispozitiv
    ├── Grafice Chart.js
    │   ├── Temperatură
    │   ├── Umiditate
    │   ├── Presiune
    │   ├── CO₂
    │   ├── PM1, PM2.5, PM10
    │   ├── Lux
    │   └── VOC
    └── Sumă ultimă măsurătoare
```

## 🔌 Conexiune la Supabase

### Configurație

Fișier: `config/supabase_client.py`

```python
# Variabile de mediu necesare:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-public-anon-key

# Client Supabase:
from config.supabase_client import get_service
service = get_service()

# Utilizare:
user = service.get_user(user_id)
devices = service.get_user_devices(user_id)
measurements = service.get_device_measurements(device_id, user_id)
```

### Bază de Date (Supabase)

**Tabele utilizate:**

1. **web_login_requests** (pentru QR login)
   - `id` (UUID, PK)
   - `user_id` (UUID, FK → users.id)
   - `status` (ENUM: PENDING, APPROVED, REJECTED)
   - `expires_at` (timestamp)
   - `consumed_at` (timestamp nullable)
   - `approved_at` (timestamp nullable)

2. **users** (din Android app)
   - `id` (UUID, PK)
   - `email` (string)
   - `created_at` (timestamp)
   - ... alte câmpuri

3. **devices** (din Android app)
   - `id` (UUID, PK)
   - `user_id` (UUID, FK → users.id)
   - `name` (string)
   - ... alte câmpuri

4. **measurements** (din Android app)
   - `id` (UUID, PK)
   - `device_id` (UUID, FK → devices.id)
   - `temperature` (float nullable)
   - `humidity` (float nullable)
   - `pressure` (float nullable)
   - `voc` (float nullable)
   - `lux` (float nullable)
   - `co2` (float nullable)
   - `pm1` (float nullable)
   - `pm25` (float nullable)
   - `pm10` (float nullable)
   - `timestamp` (timestamp)

## 🔐 Autentificare

### QR Login Flow

1. User accesează `/qr-login/`
2. Backend generează `WebLoginRequest` cu TTL 60s
3. Frontend afișează QR code cu token
4. App mobile scanează QR și trimite confirmarea la Supabase
5. Frontend se conectează la Supabase Realtime și așteptă update
6. Când app aprobă, frontend completează login cu `complete_qr_login`
7. Django stochează `supabase_user_id` în session

### Middleware de Protecție

Fișier: `config/auth_middleware.py`

- Verifica `supabase_user_id` în sesiune
- Redirect la `/qr-login/` dacă nu autentificat
- Adaugă `request.supabase_user_id` pentru acces ușor în views

## 📊 Views și URLs

### Dashboard (`/`)

- **View**: `apps/dashboard/views.py::dashboard`
- **Template**: `templates/dashboard/index.html`
- **Afișare**: Grid de card-uri cu dispozitive și ultima măsurătoare
- **Acțiuni**: Acces la dashboard detaliat, istoric

### Dashboard Dispozitiv (`/device/<device_id>/`)

- **View**: `apps/dashboard/views.py::device_dashboard`
- **Template**: `templates/dashboard/device_detail.html`
- **Afișare**: 
  - Sumă ultimă măsurătoare (6 card-uri)
  - 9 grafice Chart.js pentru toți senzori
- **Date**: Formatate ca JSON pentru JavaScript Chart.js

### Dispozitive (`/devices/`)

- **View**: `apps/devices/views.py::devices`
- **Template**: `templates/devices/index.html`
- **Afișare**: 
  - Tabel responsive cu toate dispozitivele
  - Card-uri mobile-friendly
  - Status online/offline
  - Ultima sincronizare

### Măsurători (`/measurements/device/<device_id>/`)

- **View**: `apps/measurements/views.py::history`
- **Template**: `templates/measurements/history.html`
- **Afișare**: Tabel scrollabil cu toți senzori
- **Filtrare**: Limitare la 100/500/1000 înregistrări

### Profil (`/profile/`)

- **View**: `apps/accounts/views.py::profile`
- **Template**: `templates/accounts/profile.html`
- **Afișare**: Info utilizator, acțiuni rapide

### Logout (`/qr-login/logout/`)

- **View**: `apps/qr_login/views.py::logout`
- **Template**: `templates/qr_login/logout.html`
- **Acțiune**: Curăță sesiune, redirect la login

## 🎨 Frontend

### Templates

- **base.html**: Layout principal cu navbar, Bootstrap 5, Chart.js
- **dashboard/index.html**: Grid dispozitive
- **dashboard/device_detail.html**: Grafice + tabele măsurători
- **devices/index.html**: Listă/tabel dispozitive
- **measurements/history.html**: Tabel istoric
- **accounts/profile.html**: Info utilizator
- **qr_login/start.html**: QR code + polling status
- **qr_login/logout.html**: Pagina de logout

### CSS

- Bootstrap 5 CDN
- Custom styles în base.html:
  - Cards hover effects
  - Color badges pentru status/senzori
  - Responsive grid layout
  - Chart container styling

### JavaScript

- **Chart.js** CDN pentru grafice
- **QR Login Polling**: Așteptă confirmare la fiecare 2s
- **CSRF Protection**: Cereri AJAX cu token CSRF

## ⚙️ Configurare

### settings/base.py

```python
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "apps.accounts",
    "apps.dashboard",
    "apps.measurements",
    "apps.devices",
    "apps.ai",
    "apps.qr_login",
]

MIDDLEWARE = [
    ...
    "config.auth_middleware.RequireAuthMiddleware",
]

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL")
```

### URLs Principale (config/urls.py)

```
/ → dashboard:index
/device/<id>/ → dashboard:device
/devices/ → devices:index
/measurements/device/<id>/ → measurements:history
/measurements/device/<id>/latest/ → measurements:latest_data
/profile/ → accounts:profile
/qr-login/ → qr_login:start
/qr-login/logout/ → qr_login:logout
```

## 🚀 Deployment

### Railway (din Procfile)

```
web: python manage.py migrate && gunicorn config.wsgi
```

### Variabile de Mediu

```
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<generate-long-random>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=yourdomain.com,*.railway.app
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_JWKS_URL=https://...
```

### Collectstatic

```bash
python manage.py collectstatic --noinput
```

## 📝 Siguranța Datelor

- **No Django Database Bloat**: Doar sesiuni în Django
- **All Data from Supabase**: Citire directă via supabase-py
- **RLS-Compatible**: Filtrare după `supabase_user_id`
- **Session-Based Auth**: Cookies signed cu Django SECRET_KEY
- **CSRF Protection**: Middleware standard Django
- **HTTPS Only**: `SESSION_COOKIE_SECURE=True` în production

## 🔧 Troubleshooting

### "SUPABASE_URL not set"

```bash
# .env file trebuie să conțină:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-key
```

### "Device not found or access denied"

- Verifica că device aparține utilizatorului autentificat
- Check `supabase_user_id` în sesiune
- Verifica Supabase connection

### "No measurements found"

- Verifica că dispozitivul a trimis date în Supabase
- Check `measurements` tabel pentru `device_id` corect
- Verifica filtrarea după `user_id`

## 📚 Referințe

- [Django 5 Docs](https://docs.djangoproject.com/en/5.0/)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/)
- [Chart.js](https://www.chartjs.org/docs/latest/)
