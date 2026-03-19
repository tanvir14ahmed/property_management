from __future__ import annotations

from json import dumps

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email: str, full_name: str, phone_number: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, full_name: str, phone_number: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, full_name, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=32)
    is_owner = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone_number"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    @property
    def roles(self) -> list[str]:
        roles = []
        if self.is_owner:
            roles.append("owner")
        if self.is_tenant:
            roles.append("tenant")
        return roles


class IncompleteRegistration(models.Model):
    ROLE_INTENTS = (
        (1, "Owner"),
        (2, "Tenant"),
        (3, "Owner & Tenant"),
    )

    full_name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=32)
    selected_role_intent = models.PositiveSmallIntegerField(choices=ROLE_INTENTS)
    step_reached = models.CharField(max_length=32, default="start")
    payload_json = models.JSONField(blank=True, null=True)
    otp_code = models.CharField(max_length=4, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    is_otp_verified = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Incomplete Registration"
        verbose_name_plural = "Incomplete Registrations"
        ordering = ("-created_at",)

    def mark_completed(self) -> None:
        self.is_completed = True
        self.updated_at = timezone.now()
        self.save(update_fields=("is_completed", "updated_at"))

    def __str__(self) -> str:
        return f"{self.email} ({self.get_selected_role_intent_display()})"
