# 🚀 Ghid Quick Start - Senzor de Calitate Web

## 📋 Cuprins
1. [Instalare inițială](#-instalare-inițială)
2. [Configurare](#-configurare)
3. [Pornire server](#-pornire-server)
4. [Testare QR Login](#-testare-qr-login)
5. [Troubleshooting](#-troubleshooting)

---

## 🔧 Instalare inițială

### Condiții prealabile:
- **Python 3.14+** instalat
- **pip** (package manager pentru Python)
- **Git** (opțional, pentru versionare)
- **Supabase account** (https://supabase.com) - GRATUIT

### Pasul 1: Instalare dependențe

```bash
cd "D:\senzor de calitate web"
pip install -r requirements.txt
```

Sau dacă folosești Python 3.14 explicit:
```bash
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt
```

### Pasul 2: Verifica instalarea
```bash
pip list | findstr django
pip list | findstr supabase
```

Ar trebui să vezi:
- `Django 5.2.16`
- `supabase 2.x.x` (supabase-py)

---

## ⚙️ Configurare

### Fișierul `.env` (CRITIC!)

Fișierul `.env` trebuie să conțină:

```env
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=django-insecure-dev-key-change-in-production-12345678901234567890
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Supabase (MUST BE FILLED!)
SUPABASE_URL=https://eakzxbfcwbgfxfujzote.supabase.co
SUPABASE_ANON_KEY=<YOUR_ANON_KEY_HERE>
SUPABASE_JWKS_URL=https://eakzxbfcwbgfxfujzote.supabase.co/auth/v1/.well-known/jwks.json
```

#### ⚠️ Cum să obții `SUPABASE_ANON_KEY`:

1. **Deschide**: https://app.supabase.com/project/eakzxbfcwbgfxfujzote/settings/api
2. **Caută**: Secția "Project API keys"
3. **Copiază**: Valoarea din "anon public" (NU service_role!)
4. **Lipește-o**: În `.env` la `SUPABASE_ANON_KEY=`
5. **Salvează**: Fișierul

Cheia arată așa:
```
SUPABASE_ANON_KEY=sb_publishable_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🚀 Pornire server

### ⚡ Metoda 1: Folosind Script (Cel mai simplu - RECOMANDAT)

**Dublu-click pe:**
```
run.bat  (pentru Command Prompt)
```

SAU din PowerShell:
```powershell
.\run.ps1
```

✅ Server-ul pornește automat!

Output așteptat:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL+C.
```

---

### ⚡ Metoda 2: Rulare manuală în PowerShell/CMD

```bash
cd "D:\senzor de calitate web"
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py runserver
```

⚠️ **Important:** Trebuie să folosești calea COMPLETĂ la Python (nu doar `python`)

---

### 📦 Metoda 2: CU VirtualEnv (Opțional - Mai profesional)

#### Pasul 1: Crează venv
```bash
cd "D:\senzor de calitate web"
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" -m venv venv314
```

#### Pasul 2: Activează venv
```bash
venv314\Scripts\activate
```

Vei vedea:
```
(venv314) D:\senzor de calitate web>
```

#### Pasul 3: Instalează dependencies
```bash
pip install -r requirements.txt
```

#### Pasul 4: Pornește serverul
```bash
python manage.py runserver
```

---

### Metoda 3: Cu port custom

```bash
python manage.py runserver 8080
```

Server va rula la: http://localhost:8080/

---

## 🌐 Accesare site

După pornire, site-ul este disponibil la:

👉 **http://localhost:8000/**

### Ce se întâmpla:
1. Vei fi **redirecționat automat** la pagina de login QR
2. Vei vedea **codul QR** și un **countdown de 60 de secunde**
3. Android app scanează codul
4. App aprobă login → se creează sesiune
5. Browser redirecționează la **dashboard**

---

## ✅ Testare QR Login

### Pe WebSite (Browser):
1. Accesează http://localhost:8000/
2. Ar trebui să vezi pagina cu QR code
3. Caută:
   - ✅ **Cod QR** - imagine cu coduri negre și albe
   - ✅ **Countdown** - "Codul expira în 60 secunde"
   - ✅ **Status message** - "Se așteaptă scanarea codului QR..."

### Pe Android App:
1. Deschide aplicația
2. Apasă pe **"Scan QR Code"**
3. Poziționează camera pe QR code-ul din browser
4. App citește codul
5. App aprobă conectarea
6. Browser primește notificare Realtime
7. Browser crează sesiune și redirecționează

### Test Polling Fallback (Fără Realtime):
Dacă Realtime nu funcționează:
- Browser va **verifica status din 2 în 2 secunde** (polling)
- Aceasta funcționează chiar și fără conexiune Realtime

---

## 🐛 Troubleshooting

### ❌ "Reverse for 'qr_login:start' not found"
**Soluție**: Asigură-te că restartezi serverul după editări

```bash
# CTRL-BREAK pentru a opri
# Apoi rulează din nou
python manage.py runserver
```

### ❌ "Invalid API key" (Eroare Supabase)
**Soluție**: Cheia din `.env` e greșită

```bash
# 1. Verifică cheia din dashboard Supabase
# 2. Asigură-te că e "anon public", NU "service_role"
# 3. Editează .env
# 4. Restart server
```

### ❌ "Cannot find request_id in context"
**Soluție**: Asigură-te că template-ul primește request_id din view

```python
context = {
    'request_id': request_id,
    'qr_image': qr_image,
    'supabase_url': os.getenv('SUPABASE_URL'),
    'supabase_anon_key': os.getenv('SUPABASE_ANON_KEY'),
    'expires_at': expires_at.isoformat(),
}
```

### ❌ "Port 8000 already in use"
**Soluție**: Foloseștealt port

```bash
python manage.py runserver 8080
# Apoi accesează http://localhost:8080/
```

### ❌ "ModuleNotFoundError: No module named 'supabase'"
**Soluție**: Reinstalează dependențele

```bash
pip install supabase --upgrade
pip install -r requirements.txt
```

### ❌ QR code nu se afișează (doar text)
**Soluție**: Asigură-te că qrcode library e instalat

```bash
pip install qrcode[pil]
```

---

## 📊 Structura Proiectului

```
d:\senzor de calitate web\
├── manage.py                      # Django management script
├── requirements.txt               # Dependencies
├── .env                          # Configuration (GITIGNORE!)
├── .gitignore                    # Files to ignore
│
├── config/
│   ├── settings/
│   │   ├── base.py              # Base Django settings
│   │   ├── local.py             # Local development
│   │   └── production.py        # Production settings
│   ├── supabase_client.py        # Supabase service layer
│   ├── auth_middleware.py        # Session validation
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI for gunicorn
│   └── asgi.py                  # ASGI for async
│
└── apps/
    ├── qr_login/                # QR Login feature
    │   ├── views.py             # start(), check_status(), complete_login()
    │   ├── urls.py              # URL patterns
    │   ├── models.py            # (Optional) Database models
    │   ├── services.py          # Business logic
    │   └── templates/
    │       └── qr_login/
    │           └── start.html   # QR display page
    │
    ├── dashboard/               # Main dashboard
    ├── devices/                 # Device management
    ├── measurements/            # Sensor readings
    ├── accounts/                # User profiles
    └── ai/                      # AI features
```

---

## 🔑 Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `DJANGO_DEBUG` | Enable debug mode (development only) | `true` |
| `DJANGO_SECRET_KEY` | Django encryption key | `django-insecure-...` |
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Public API key | `sb_publishable_...` |

⚠️ **NEVER commit `.env` to Git!** (Already in .gitignore)

---

## 🚀 Production Deployment

### Rulează migrations:
```bash
python manage.py migrate
```

### Collect static files:
```bash
python manage.py collectstatic --noinput
```

### Folosește gunicorn (în loc de runserver):
```bash
pip install gunicorn
gunicorn config.wsgi --bind 0.0.0.0:8000
```

### Deploy pe Railway.app:
```bash
# Railway va folosi Procfile:
# web: gunicorn config.wsgi
```

---

## 📞 Comenzi Utile

```bash
# Start server (using full Python path)
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py runserver

# OR use the script
run.bat  # Windows Command Prompt
.\run.ps1  # PowerShell

# Apply migrations
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py migrate

# Create superuser (admin)
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py createsuperuser

# Access Django shell
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py shell

# Collect static files
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py collectstatic

# Run tests
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py test

# Check for issues
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" manage.py check

# Install dependencies
"C:\Users\Sebi\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt
```

---

## 🎯 Checklist Înainte de Prima Rulare

- [ ] `.env` completat cu cheia Supabase reală
- [ ] Python 3.14+ instalat la: `C:\Users\Sebi\AppData\Local\Programs\Python\Python314\`
- [ ] `pip install -r requirements.txt` executat
- [ ] Supabase project creat și tabel `web_login_requests` gata
- [ ] Server pornit cu `run.bat` sau comanda manuală
- [ ] Browser accesează http://localhost:8000/ 
- [ ] Văd pagina cu QR code și countdown

---

## 📚 Resurse Utile

- **Django Docs**: https://docs.djangoproject.com/
- **Supabase Docs**: https://supabase.com/docs
- **Supabase-py Docs**: https://github.com/supabase-community/supabase-py
- **Supabase Realtime**: https://supabase.com/docs/guides/realtime

---

## 💬 Notă

Dacă ai orice problemă, verifică:
1. **Terminal output** pentru erori
2. **Browser console** (F12) pentru JavaScript errors
3. **Django debug page** (DJANGO_DEBUG=true)

**Server-ul ești gata! Baftă! 🚀**
