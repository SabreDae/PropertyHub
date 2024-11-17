from .base import *

DEBUG = False
ALLOWED_HOSTS = []  # TODO: Add production host(s)

CORS_ALLOWED_ORIGINS = []  # TODO: Add allowed origins

DATABASES = {}  # TODO: Add production database configuration

# Security Settings - ensure HTTP redirect to HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True