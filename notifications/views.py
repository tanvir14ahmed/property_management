from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related("related_object_type")


def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.mark_read()
    return redirect(request.META.get("HTTP_REFERER", "notifications:list"))


def mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")


def clear_read_notifications(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=True).delete()
    return redirect(request.META.get("HTTP_REFERER", "notifications:list"))


def unread_count_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"count": 0})
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"count": count})
