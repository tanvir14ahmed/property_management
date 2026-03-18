from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    apartment = models.OneToOneField("properties.Apartment", on_delete=models.CASCADE, related_name="conversation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Chat for {self.apartment.apartment_code}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_text = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def mark_read(self):
        self.is_read = True
        self.read_at = timezone.now()

    def __str__(self) -> str:
        return f"{self.sender.email} @ {self.created_at:%Y-%m-%d %H:%M}"
