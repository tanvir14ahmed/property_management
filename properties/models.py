from __future__ import annotations

from datetime import date

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from core.services import generate_apartment_code, generate_building_code


class Building(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="buildings")
    building_name = models.CharField(max_length=255)
    building_code = models.CharField(max_length=8, unique=True, editable=False)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=32)
    country = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.building_code:
            self.building_code = generate_building_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.building_name} ({self.building_code})"


class Apartment(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="apartments")
    apartment_name = models.CharField(max_length=255)
    apartment_code = models.CharField(max_length=8, unique=True, editable=False)
    floor_number = models.IntegerField(null=True, blank=True)
    bedrooms = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    square_feet = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.apartment_code:
            self.apartment_code = generate_apartment_code()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.apartment_name} ({self.apartment_code})"

    @property
    def active_assignment(self):
        return self.assignments.filter(is_active=True).first()


class TenantJoinRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    )

    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="join_requests")
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="join_requests")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_requests")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "apartment"),
                condition=Q(status="pending"),
                name="unique_pending_join_request",
            )
        ]

    def __str__(self) -> str:
        return f"{self.tenant.email} -> {self.apartment.apartment_code} ({self.status})"


class ApartmentOccupancy(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="assignments")
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="occupancies")
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="approvals")
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("apartment", "tenant", "start_date")

    def __str__(self) -> str:
        return f"{self.tenant.email} in {self.apartment.apartment_code}"
