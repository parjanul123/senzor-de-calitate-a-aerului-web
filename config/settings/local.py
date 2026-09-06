import os

from .base import *

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", SECRET_KEY)
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [
	host.strip()
	for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
	if host.strip()
]
ALLOWED_HOSTS.append(".up.railway.app")

railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
if railway_public_domain:
	ALLOWED_HOSTS.append(railway_public_domain)

SUPABASE_URL = os.getenv("SUPABASE_URL", SUPABASE_URL)
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", SUPABASE_ANON_KEY)
SUPABASE_SERVICE_ROLE_KEY = (
	os.getenv("SUPABASE_SERVICE_ROLE_KEY")
	or os.getenv("SUPABASE_SERVICE_KEY")
	or SUPABASE_SERVICE_ROLE_KEY
)
SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL", SUPABASE_JWKS_URL)

# For development, use standard static files storage (no hashing/compression)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"