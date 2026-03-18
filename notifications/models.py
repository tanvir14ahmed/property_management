from __future__ import annotations

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    message = models.TextField()
    related_object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey("related_object_type", "related_object_id")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def mark_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=("is_read", "read_at"))

    def __str__(self) -> str:
        return f"{self.title} → {self.user.email}"
