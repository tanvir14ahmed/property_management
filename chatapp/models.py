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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.broadcast_unread_count()

    def broadcast_unread_count(self):
        """Broadcasts the unread message count to the recipient."""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            
            # Recipient is the person in the conversation who is NOT the sender
            # Owner <-> Tenant
            apartment = self.conversation.apartment
            recipient = None
            if self.sender == apartment.building.owner:
                # Recipient is the tenant
                active_assignment = apartment.active_assignment
                if active_assignment:
                    recipient = active_assignment.tenant
            else:
                # Recipient is the owner
                recipient = apartment.building.owner

            if recipient:
                # Count unread messages for recipient
                from .models import Message
                count = Message.objects.filter(
                    conversation__apartment__is_active=True,
                    is_read=False
                ).exclude(sender=recipient).distinct().count() or 0

                async_to_sync(channel_layer.group_send)(
                    f"user_notifications_{recipient.id}",
                    {
                        "type": "send_notification",
                        "unread_messages": count,
                    }
                )
        except Exception:
            pass

    def mark_read(self):
        self.is_read = True
        self.read_at = timezone.now()

    def __str__(self) -> str:
        return f"{self.sender.email} @ {self.created_at:%Y-%m-%d %H:%M}"
