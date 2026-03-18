from __future__ import annotations

from django.contrib import admin

from .models import Apartment, ApartmentOccupancy, Building, TenantJoinRequest


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("building_name", "building_code", "owner", "city", "is_active")
    search_fields = ("building_name", "building_code", "city")
    list_filter = ("is_active", "city")


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ("apartment_name", "apartment_code", "building", "is_active", "is_occupied")
    search_fields = ("apartment_name", "apartment_code")
    list_filter = ("is_active", "is_occupied")


@admin.register(TenantJoinRequest)
class TenantJoinRequestAdmin(admin.ModelAdmin):
    list_display = ("tenant", "apartment", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("tenant__email", "apartment__apartment_code")


@admin.register(ApartmentOccupancy)
class ApartmentOccupancyAdmin(admin.ModelAdmin):
    list_display = ("tenant", "apartment", "is_active", "start_date", "end_date")
    list_filter = ("is_active",)
    search_fields = ("tenant__email", "apartment__apartment_code")
