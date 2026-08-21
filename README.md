# Senzor de calitate web

Backend Django 5 pentru monitorizarea calitatii aerului. Aplicatia web foloseste aceeasi baza PostgreSQL Supabase ca aplicatia Android. Identitatea utilizatorilor este furnizata exclusiv de Supabase Auth; autentificarea Django nu este activata.

## Aplicatii

- `accounts`: integrarea cu Supabase Auth si profiluri web.
- `dashboard`: sumarizari si vizualizari de monitorizare.
- `devices`: dispozitive, senzori si masuratori.
- `ai`: analize si predictii.
- `qr_login`: flux de autentificare bazat pe cod QR.

## Pornire locala

1. Creeaza un mediu virtual: `py -m venv .venv`
2. Activeaza-l: `.\.venv\Scripts\Activate.ps1`
3. Instaleaza dependintele: `py -m pip install -r requirements.txt`
4. Copiaza `.env.example` in `.env` si configureaza valorile Supabase.
5. Seteaza `DATABASE_URL` cu connection string-ul PostgreSQL Supabase; este obligatoriu.
6. Ruleaza: `py manage.py runserver`

Nu exista fallback SQLite. Django se opreste explicit daca `DATABASE_URL` lipseste, astfel incat site-ul foloseste numai baza PostgreSQL Supabase comuna cu aplicatia Android. Pornirea aplicatiei nu creeaza si nu modifica tabele; orice migrare trebuie rulata deliberat dupa verificarea ei.

## Railway

Seteaza in Railway variabilele `DJANGO_SETTINGS_MODULE=config.settings.production`, `DJANGO_SECRET_KEY`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `DJANGO_ALLOWED_HOSTS` si `DJANGO_CSRF_TRUSTED_ORIGINS`. Configuratia Railway ruleaza migrarile si colecteaza fisierele statice inaintea pornirii Gunicorn.