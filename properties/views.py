from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ApartmentForm, BuildingForm
from .models import Apartment, ApartmentOccupancy, Building, TenantJoinRequest


# ─── Mixins ───────────────────────────────────────────────────────────────────

class OwnerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_owner:
            messages.error(request, "You need an Owner account to access this page.")
            return redirect("core:dashboard")
        return super().dispatch(request, *args, **kwargs)


# ─── Public Listings ────────────────────────────────────────────────────────────

class PublicListingView(ListView):
    model = Apartment
    template_name = "properties/public_list.html"
    context_object_name = "apartments"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        qs = Apartment.objects.filter(is_active=True, is_occupied=False).select_related("building")
        if q:
            qs = qs.filter(Q(building__city__icontains=q) | Q(apartment_name__icontains=q) | Q(building__building_name__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


# ─── Buildings ────────────────────────────────────────────────────────────────

class BuildingListView(LoginRequiredMixin, ListView):
    model = Building
    template_name = "properties/building_list.html"
    context_object_name = "buildings"

    def get_queryset(self):
        qs = Building.objects.filter(owner=self.request.user, is_active=True).annotate(
            apartment_count=Count("apartments"),
            occupied_count=Count("apartments", filter=Q(apartments__is_occupied=True)),
        )
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(building_name__icontains=q) | Q(building_code__icontains=q) | Q(city__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class BuildingCreateView(OwnerRequiredMixin, CreateView):
    model = Building
    form_class = BuildingForm
    template_name = "properties/building_form.html"
    success_url = reverse_lazy("properties:building_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Building created successfully.")
        return super().form_valid(form)


class BuildingDetailView(LoginRequiredMixin, DetailView):
    model = Building
    template_name = "properties/building_detail.html"
    context_object_name = "building"

    def get_queryset(self):
        return Building.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["apartments"] = self.object.apartments.filter(is_active=True).select_related()
        ctx["pending_requests"] = TenantJoinRequest.objects.filter(building=self.object, status="pending").select_related("tenant", "apartment")
        return ctx


class BuildingUpdateView(OwnerRequiredMixin, UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = "properties/building_form.html"

    def get_queryset(self):
        return Building.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("properties:building_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Building updated.")
        return super().form_valid(form)


# ─── Apartments ───────────────────────────────────────────────────────────────

class ApartmentCreateView(OwnerRequiredMixin, CreateView):
    model = Apartment
    form_class = ApartmentForm
    template_name = "properties/apartment_form.html"

    def get_building(self):
        return get_object_or_404(Building, pk=self.kwargs["building_pk"], owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["building"] = self.get_building()
        return ctx

    def form_valid(self, form):
        form.instance.building = self.get_building()
        messages.success(self.request, "Apartment added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("properties:building_detail", kwargs={"pk": self.kwargs["building_pk"]})


class ApartmentDetailView(LoginRequiredMixin, DetailView):
    model = Apartment
    template_name = "properties/apartment_detail.html"
    context_object_name = "apartment"

    def get_queryset(self):
        return Apartment.objects.filter(building__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["occupancy"] = self.object.active_assignment
        ctx["join_requests"] = self.object.join_requests.filter(status="pending").select_related("tenant")
        ctx["payment_requests"] = self.object.payment_requests.order_by("-created_at")[:5]
        ctx["issues"] = self.object.issues.order_by("-created_at")[:5]
        return ctx


class ApartmentUpdateView(OwnerRequiredMixin, UpdateView):
    model = Apartment
    form_class = ApartmentForm
    template_name = "properties/apartment_form.html"

    def get_queryset(self):
        return Apartment.objects.filter(building__owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["building"] = self.object.building
        return ctx

    def get_success_url(self):
        return reverse_lazy("properties:apartment_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Apartment updated.")
        return super().form_valid(form)


class UploadLeaseView(OwnerRequiredMixin, UpdateView):
    model = ApartmentOccupancy
    fields = ["lease_document"]
    template_name = "properties/lease_form.html"

    def get_queryset(self):
        return ApartmentOccupancy.objects.filter(apartment__building__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy("properties:apartment_detail", kwargs={"pk": self.object.apartment.pk})

    def form_valid(self, form):
        messages.success(self.request, "Lease document uploaded successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["apartment"] = self.object.apartment
        ctx["tenant"] = self.object.tenant
        return ctx


# ─── Tenant Join Request Actions ──────────────────────────────────────────────

class JoinRequestListView(LoginRequiredMixin, ListView):
    template_name = "properties/join_request_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        return TenantJoinRequest.objects.filter(
            building__owner=self.request.user, status="pending"
        ).select_related("tenant", "apartment", "building").order_by("-created_at")


def approve_join_request(request, pk):
    if not request.user.is_authenticated or not request.user.is_owner:
        return redirect("core:dashboard")
    jr = get_object_or_404(TenantJoinRequest, pk=pk, building__owner=request.user, status="pending")
    
    from django.utils import timezone
    from core.services import create_notification
    
    jr.status = "approved"
    jr.reviewed_by = request.user
    jr.reviewed_at = timezone.now()
    jr.save()

    # Deactivate any previous occupancy for this apartment
    ApartmentOccupancy.objects.filter(apartment=jr.apartment, is_active=True).update(is_active=False)

    # Create new occupancy
    ApartmentOccupancy.objects.create(
        apartment=jr.apartment,
        tenant=jr.tenant,
        approved_by=request.user,
        approved_at=timezone.now(),
        is_active=True,
    )

    jr.apartment.is_occupied = True
    jr.apartment.save(update_fields=["is_occupied"])

    create_notification(
        f"Your join request for {jr.apartment.apartment_name} has been approved!",
        jr.tenant,
        related=jr,
    )

    if request.headers.get("HX-Request"):
        pending_requests = TenantJoinRequest.objects.filter(building=jr.building, status="pending").select_related("tenant", "apartment")
        return render(request, "properties/partials/join_requests.html", {"pending_requests": pending_requests})
        
    return redirect(request.META.get("HTTP_REFERER", "properties:join_request_list"))


def reject_join_request(request, pk):
    if not request.user.is_authenticated or not request.user.is_owner:
        return redirect("core:dashboard")
    jr = get_object_or_404(TenantJoinRequest, pk=pk, building__owner=request.user, status="pending")
    
    from django.utils import timezone
    from core.services import create_notification

    jr.status = "rejected"
    jr.reviewed_by = request.user
    jr.reviewed_at = timezone.now()
    jr.save()

    create_notification(
        f"Your join request for {jr.apartment.apartment_name} was not approved this time.",
        jr.tenant,
        related=jr,
    )
    if request.headers.get("HX-Request"):
        pending_requests = TenantJoinRequest.objects.filter(building=jr.building, status="pending").select_related("tenant", "apartment")
        return render(request, "properties/partials/join_requests.html", {"pending_requests": pending_requests})

    messages.warning(request, f"Rejected join request from {jr.tenant.full_name}.")
    return redirect(request.META.get("HTTP_REFERER", "properties:join_request_list"))


# ─── Tenant: Search & Request ─────────────────────────────────────────────────

class ApartmentSearchView(LoginRequiredMixin, ListView):
    template_name = "properties/apartment_search.html"
    context_object_name = "results"

    def get_queryset(self):
        mode = self.request.GET.get("mode", "building")
        code = self.request.GET.get("code", "").strip().upper()
        if not code:
            return Apartment.objects.none()
        if mode == "apartment":
            return Apartment.objects.filter(apartment_code=code, is_active=True).select_related("building")
        return Apartment.objects.filter(building__building_code=code, is_active=True).select_related("building")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["mode"] = self.request.GET.get("mode", "building")
        ctx["code"] = self.request.GET.get("code", "")
        ctx["searched"] = bool(self.request.GET.get("code"))
        # For each result, check if the user already has a pending request
        existing = set(
            TenantJoinRequest.objects.filter(
                tenant=self.request.user, status="pending"
            ).values_list("apartment_id", flat=True)
        )
        ctx["existing_requests"] = existing
        return ctx


def submit_join_request(request, apartment_pk):
    if not request.user.is_authenticated or not request.user.is_tenant:
        messages.error(request, "You need a Tenant account to submit a join request.")
        return redirect("core:dashboard")
    
    apartment = get_object_or_404(Apartment, pk=apartment_pk, is_active=True)

    if TenantJoinRequest.objects.filter(tenant=request.user, apartment=apartment, status="pending").exists():
        messages.warning(request, "You already have a pending request for this apartment.")
        return redirect("properties:search")

    jr = TenantJoinRequest.objects.create(
        tenant=request.user,
        building=apartment.building,
        apartment=apartment,
        message=request.POST.get("message", ""),
    )

    from core.services import create_notification
    create_notification(
        f"{request.user.full_name} requested to join apartment {apartment.apartment_code}.",
        apartment.building.owner,
        related=jr,
    )
    messages.success(request, f"Join request sent for {apartment.apartment_name}.")
    return redirect("properties:search")
