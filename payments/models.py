from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class PaymentRequest(models.Model):
    PAYMENT_TYPES = (
        ("rent", "Rent"),
        ("electricity", "Electricity"),
        ("water", "Water"),
        ("gas", "Gas"),
        ("maintenance", "Maintenance"),
        ("other", "Other"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("marked_paid", "Marked Paid"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    )

    building = models.ForeignKey(
        "properties.Building",
        on_delete=models.PROTECT,
        related_name="payment_requests",
    )
    apartment = models.ForeignKey(
        "properties.Apartment",
        on_delete=models.PROTECT,
        related_name="payment_requests",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_payments",
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tenant_payments",
    )
    title = models.CharField(max_length=128)
    payment_type = models.CharField(max_length=32, choices=PAYMENT_TYPES)
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def mark_paid(self) -> None:
        self.status = "marked_paid"
        self.save(update_fields=("status", "updated_at"))

    def __str__(self) -> str:
        return f"{self.title} ({self.payment_type}) - {self.amount}"


class PaymentConfirmation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    payment_request = models.ForeignKey(
        PaymentRequest,
        on_delete=models.CASCADE,
        related_name="confirmations",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_confirmations",
    )
    payment_method_text = models.CharField(max_length=128)
    note = models.TextField(blank=True)
    proof_image = models.ImageField(upload_to="payments/proofs/", blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payment_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.payment_request} confirmation ({self.status})"

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        if self.status == "approved":
            if not hasattr(self, "invoice"):
                from .services import handle_payment_approval

                handle_payment_approval(self)


class Invoice(models.Model):
    payment_request = models.OneToOneField(
        PaymentRequest,
        on_delete=models.CASCADE,
        related_name="invoice",
    )
    payment_confirmation = models.OneToOneField(
        PaymentConfirmation,
        on_delete=models.CASCADE,
        related_name="invoice",
    )
    invoice_number = models.CharField(max_length=32, unique=True)
    invoice_date = models.DateField(default=timezone.now)
    owner_copy_pdf = models.CharField(max_length=255, blank=True)
    tenant_copy_pdf = models.CharField(max_length=255, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.invoice_number


class Expense(models.Model):
    EXPENSE_TYPES = (
        ("maintenance", "Maintenance"),
        ("repair", "Repair"),
        ("utility", "Utility Bill"),
        ("services", "Service/Staff"),
        ("other", "Other"),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="property_expenses",
    )
    building = models.ForeignKey(
        "properties.Building",
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    apartment = models.ForeignKey(
        "properties.Apartment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    title = models.CharField(max_length=128)
    expense_type = models.CharField(max_length=32, choices=EXPENSE_TYPES, default="maintenance")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to="payments/expenses/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date", "-created_at")

    def __str__(self) -> str:
        return f"{self.title} - {self.amount}"
