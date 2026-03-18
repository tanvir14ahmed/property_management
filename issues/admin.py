from __future__ import annotations

from django.contrib import admin

from .models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "owner", "status", "priority", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("title", "tenant__email", "owner__email")
