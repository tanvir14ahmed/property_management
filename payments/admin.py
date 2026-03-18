from __future__ import annotations

from django.contrib import admin

from .models import Invoice, PaymentConfirmation, PaymentRequest


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "payment_type", "tenant", "status", "amount", "due_date")
    list_filter = ("payment_type", "status")
    search_fields = ("title", "tenant__email", "apartment__apartment_code")


@admin.register(PaymentConfirmation)
class PaymentConfirmationAdmin(admin.ModelAdmin):
    list_display = ("payment_request", "submitted_by", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("payment_request__title", "submitted_by__email")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "payment_request", "invoice_date", "total")
    search_fields = ("invoice_number", "payment_request__title")
