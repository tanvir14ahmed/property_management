from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from properties.models import Apartment


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        buildings = user.buildings.filter(is_active=True)
        pending_payments = user.tenant_payments.filter(status="pending").count()
        context.update(
            roles=user.roles if hasattr(user, "roles") else [],
            building_count=buildings.count(),
            apartment_count=Apartment.objects.filter(building__in=buildings).count(),
            pending_requests=user.join_requests.filter(status="pending").count(),
            open_issues=user.owner_issues.filter(status__in=["open", "in_progress"]).count(),
            pending_payments=pending_payments,
            recent_notifications=user.notifications.select_related("related_object_type")[:3],
        )
        return context
