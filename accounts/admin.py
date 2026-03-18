from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import IncompleteRegistration, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("email", "full_name", "is_owner", "is_tenant", "is_staff", "is_active")
    list_filter = ("is_owner", "is_tenant", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal information", {"fields": ("full_name", "phone_number")}),
        ("Roles", {"fields": ("is_owner", "is_tenant")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "phone_number", "password1", "password2", "is_owner", "is_tenant"),
            },
        ),
    )
    search_fields = ("email", "full_name", "phone_number")
    ordering = ("email",)


@admin.register(IncompleteRegistration)
class IncompleteRegistrationAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name", "selected_role_intent", "step_reached", "is_completed", "created_at")
    list_filter = ("selected_role_intent", "is_completed")
    search_fields = ("email", "full_name", "phone_number")
    readonly_fields = ("created_at", "updated_at")
