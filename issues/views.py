from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import IssueForm
from .models import Issue


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = "issues/list.html"
    context_object_name = "issues"

    def get_queryset(self):
        user = self.request.user
        if user.is_owner:
            return Issue.objects.filter(owner=user)
        if user.is_tenant:
            return Issue.objects.filter(tenant=user)
        return Issue.objects.none()


class IssueCreateView(LoginRequiredMixin, CreateView):
    model = Issue
    form_class = IssueForm
    template_name = "issues/create.html"
    success_url = reverse_lazy("issues:list")

    def form_valid(self, form):
        form.instance.tenant = self.request.user
        if form.instance.building.owner != self.request.user:
            form.instance.owner = form.instance.building.owner
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Issue submitted; owner notified.")
        return super().get_success_url()


@login_required
def resolve_issue(request, pk):
    """Owner marks issue as resolved (awaiting approval)."""
    issue = get_object_or_404(Issue, pk=pk, owner=request.user)
    issue.mark_resolved()
    issue.notify_resolution_request()
    messages.success(request, f"Issue '{issue.title}' marked as resolved. Awaiting tenant approval.")
    return redirect("issues:list")


@login_required
def approve_issue(request, pk):
    """Tenant confirms the issue is solved."""
    issue = get_object_or_404(Issue, pk=pk, tenant=request.user)
    issue.mark_solved()
    issue.notify_solved()
    messages.success(request, f"Issue '{issue.title}' confirmed as solved.")
    return redirect("issues:list")


from django.views.generic import UpdateView

class IssueAssignVendorView(LoginRequiredMixin, UpdateView):
    model = Issue
    from .forms import IssueAssignVendorForm
    form_class = IssueAssignVendorForm
    template_name = "issues/assign_vendor_form.html"
    success_url = reverse_lazy("issues:list")

    def get_queryset(self):
        return Issue.objects.filter(owner=self.request.user)
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs
        
    def form_valid(self, form):
        messages.success(self.request, "Vendor assigned to issue.")
        return super().form_valid(form)


from .models import Vendor
from .forms import VendorForm

class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = "issues/vendor_list.html"
    context_object_name = "vendors"

    def get_queryset(self):
        return Vendor.objects.filter(owner=self.request.user)

class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = "issues/vendor_form.html"
    success_url = reverse_lazy("issues:vendor_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Vendor added.")
        return super().form_valid(form)

class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = "issues/vendor_form.html"
    success_url = reverse_lazy("issues:vendor_list")

    def get_queryset(self):
        return Vendor.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Vendor updated.")
        return super().form_valid(form)
