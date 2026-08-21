import os

from .base import *

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", SECRET_KEY)
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")

SUPABASE_URL = os.getenv("SUPABASE_URL", SUPABASE_URL)
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", SUPABASE_ANON_KEY)
SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL", SUPABASE_JWKS_URL)

# For development, use standard static files storage (no hashing/compression)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"