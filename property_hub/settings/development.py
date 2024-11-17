from .base import *


DEBUG = True

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

CORS_ALLOW_ALL_ORIGINS = True


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}