from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from properties.models import Apartment


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request"):
            part = request.GET.get("part")
            if part == "stats":
                return render(request, "core/partials/stats.html", self.get_context_data())
            elif part == "activity":
                return render(request, "core/partials/activity.html", self.get_context_data())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        buildings = user.buildings.filter(is_active=True)
        
        # Consistent fetching for both full and partial views
        pending_payments = 0
        if hasattr(user, 'tenant_payments'):
             pending_payments = user.tenant_payments.filter(status="pending").count()
             
        context.update(
            roles=user.roles if hasattr(user, "roles") else [],
            building_count=buildings.count(),
            apartment_count=Apartment.objects.filter(building__in=buildings).count(),
            pending_requests=user.join_requests.filter(status="pending").count() if hasattr(user, 'join_requests') else 0,
            open_issues=user.owner_issues.filter(status__in=["open", "in_progress"]).count() if hasattr(user, 'owner_issues') else 0,
            pending_payments=pending_payments,
            recent_notifications=user.notifications.all().select_related("related_object_type")[:3] if hasattr(user, 'notifications') else [],
        )
        return context
