from __future__ import annotations

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
