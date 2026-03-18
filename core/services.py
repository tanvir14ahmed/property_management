from __future__ import annotations

import random
import string
from datetime import datetime

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models


def _generate_code(prefix: str, length: int = 7) -> str:
    body = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{body}"


def generate_building_code() -> str:
    return _generate_code("B")


def generate_apartment_code() -> str:
    return _generate_code("A")


def generate_invoice_number(counter: int | None = None) -> str:
    date_part = datetime.utcnow().strftime("%Y%m%d")
    seq = f"{counter or random.randint(1, 999999):06d}"
    return f"INV-{date_part}-{seq}"


def create_notification(message: str, user: models.Model, related: models.Model | None = None) -> None:
    content_type = None
    object_id = None
    if related is not None:
        content_type = ContentType.objects.get_for_model(related)
        object_id = related.pk
    Notification = apps.get_model("notifications", "Notification")
    if Notification is None:
        return
    Notification.objects.create(
        user=user,
        title=message[:64],
        message=message,
        related_object_type=content_type,
        related_object_id=object_id,
    )
