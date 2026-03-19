from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from core.services import create_notification


class Vendor(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendors")
    name = models.CharField(max_length=128)
    specialty = models.CharField(max_length=64, help_text="e.g. Plumber, Electrician")
    phone_number = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.specialty})"


class Issue(models.Model):
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    )
    STATUS_CHOICES = (
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Awaiting Approval"),
        ("solved", "Fully Solved"),
        ("closed", "Closed"),
    )

    apartment = models.ForeignKey("properties.Apartment", on_delete=models.PROTECT, related_name="issues")
    building = models.ForeignKey("properties.Building", on_delete=models.PROTECT, related_name="issues")
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_issues")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner_issues")
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="open")
    image = models.ImageField(upload_to="issues/images/", blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues")
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def mark_resolved(self) -> None:
        """Called by Owner to indicate work is done."""
        self.status = "resolved"
        self.save(update_fields=("status", "updated_at"))

    def mark_solved(self) -> None:
        """Called by Tenant to confirm the fix."""
        self.status = "solved"
        self.resolved_at = timezone.now()
        self.save(update_fields=("status", "resolved_at", "updated_at"))

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating:
            self.notify_creation()

    def notify_creation(self) -> None:
        message = f"Issue '{self.title}' raised by {self.tenant.full_name}."
        create_notification(message, self.owner, related=self)
        try:
            send_mail(
                subject=f"[Issue] {self.title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.owner.email],
                fail_silently=True,
            )
        except Exception:
            pass

    def notify_resolution_request(self) -> None:
        message = f"Owner has marked issue '{self.title}' as resolved. Please approve."
        create_notification(message, self.tenant, related=self)

    def notify_solved(self) -> None:
        message = f"Issue '{self.title}' has been fully solved and approved."
        create_notification(message, self.owner, related=self)

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"
