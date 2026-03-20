from __future__ import annotations

from django.urls import path

from . import views
from .views import ChatListView, ChatRoomView

app_name = "chatapp"

urlpatterns = [
    path("", ChatListView.as_view(), name="list"),
    path("apartments/<int:pk>/", ChatRoomView.as_view(), name="apartment_chat"),
    path("api/unread-count/", views.unread_message_count_api, name="unread_count_api"),
]
