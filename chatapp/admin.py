from __future__ import annotations

from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("apartment", "created_at")
    search_fields = ("apartment__apartment_code",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "created_at")
    search_fields = ("conversation__apartment__apartment_code", "sender__email")
