from __future__ import annotations

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
import os
EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
