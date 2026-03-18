from __future__ import annotations

from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("<int:pk>/read/", views.mark_notification_read, name="mark_read"),
    path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
    path("api/unread-count/", views.unread_count_api, name="unread_count_api"),
]
