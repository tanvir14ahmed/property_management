from __future__ import annotations

import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()
]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "True").lower() in {"1", "true", "yes"}
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "60"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() in {
    "1",
    "true",
    "yes",
}
SECURE_HSTS_PRELOAD = os.getenv("DJANGO_SECURE_HSTS_PRELOAD", "False").lower() in {"1", "true", "yes"}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
