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

    def get_target_url(self):
        """Returns the URL this notification should point to."""
        if not self.related_object:
            return None
        
        try:
            # Handle different content types
            model_name = self.related_object_type.model
            if model_name == 'issue':
                from django.urls import reverse
                return f"{reverse('issues:list')}?open_issue={self.related_object_id}"
            elif model_name == 'tenantjoinrequest':
                from django.urls import reverse
                return reverse('properties:building_detail', kwargs={'pk': self.related_object.building.pk})
            elif model_name == 'paymentrequest':
                from django.urls import reverse
                return reverse('payments:list')
            elif model_name == 'apartment':
                from django.urls import reverse
                return reverse('properties:apartment_detail', kwargs={'pk': self.related_object.pk})
            
            # Default fallback to absolute url if exists
            if hasattr(self.related_object, 'get_absolute_url'):
                return self.related_object.get_absolute_url()
        except Exception:
            pass
        return None

    def __str__(self) -> str:
        return f"{self.title} → {self.user.email}"
