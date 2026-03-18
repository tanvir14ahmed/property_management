from __future__ import annotations
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import ExpenseForm, PaymentConfirmationForm, PaymentRequestForm
from .models import Expense, PaymentConfirmation, PaymentRequest
from .services import generate_financial_statement


class PaymentRequestListView(LoginRequiredMixin, ListView):
    model = PaymentRequest
    template_name = "payments/list.html"
    context_object_name = "requests"

    def get_queryset(self):
        user = self.request.user
        if user.is_owner:
            return PaymentRequest.objects.filter(owner=user)
        if user.is_tenant:
            return PaymentRequest.objects.filter(tenant=user)
        return PaymentRequest.objects.none()


class PaymentRequestCreateView(LoginRequiredMixin, CreateView):
    model = PaymentRequest
    form_class = PaymentRequestForm
    template_name = "payments/create.html"
    success_url = reverse_lazy("payments:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        
        # Security check: Does user own the building?
        if form.instance.building.owner != user:
            form.add_error("building", "You must own the selected building.")
            return self.form_invalid(form)
            
        # Security check: Does the apartment belong to the building?
        if form.instance.apartment.building != form.instance.building:
            form.add_error("apartment", "The selected apartment does not belong to this building.")
            return self.form_invalid(form)

        # Automatically assign tenant from active occupancy
        assignment = form.instance.apartment.active_assignment
        if not assignment:
            form.add_error("apartment", "This apartment currently has no active tenant.")
            return self.form_invalid(form)
            
        form.instance.tenant = assignment.tenant
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Could not create request; please fix the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from properties.models import Apartment
        apartments = Apartment.objects.filter(building__owner=self.request.user).values("id", "building_id", "apartment_name", "apartment_code")
        context["apartment_map"] = list(apartments)
        return context


class PaymentRequestDetailView(LoginRequiredMixin, DetailView):
    model = PaymentRequest
    template_name = "payments/detail.html"
    context_object_name = "payment_request"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_owner:
            qs = qs.filter(owner=user)
        elif user.is_tenant:
            qs = qs.filter(tenant=user)
        else:
            qs = qs.none()
        return qs


class PaymentConfirmationCreateView(LoginRequiredMixin, CreateView):
    model = PaymentConfirmation
    form_class = PaymentConfirmationForm
    template_name = "payments/confirm.html"

    def dispatch(self, request, *args, **kwargs):
        self.payment_request = get_object_or_404(PaymentRequest, pk=kwargs["pk"])
        
        # Security: Only the assigned tenant
        if request.user != self.payment_request.tenant:
            messages.error(request, "Only the assigned tenant may confirm a payment.")
            return redirect("payments:list")
            
        # Business Logic: One confirmation 1 time for 1 payment Request.
        if self.payment_request.confirmations.exists():
            messages.warning(request, "A payment confirmation already exists for this request.")
            return redirect("payments:detail", pk=self.payment_request.pk)

        # Business Logic: No body can Edit/Confirm if already Approved/Solved.
        if self.payment_request.status == "approved":
            messages.info(request, "This payment is already fully solved and locked.")
            return redirect("payments:detail", pk=self.payment_request.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.payment_request = self.payment_request
        form.instance.submitted_by = self.request.user
        form.instance.status = "pending"
        messages.success(self.request, "Payment confirmation submitted. Awaiting owner review.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("payments:detail", kwargs={"pk": self.payment_request.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_request"] = self.payment_request
        return context


from django.views.generic import UpdateView

class PaymentConfirmationUpdateView(LoginRequiredMixin, UpdateView):
    model = PaymentConfirmation
    form_class = PaymentConfirmationForm
    template_name = "payments/confirm.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Security: Only the person who submitted
        if request.user != self.object.submitted_by:
            messages.error(request, "You cannot edit this confirmation.")
            return redirect("payments:detail", pk=self.object.payment_request.pk)
            
        # Business Logic: Cannot edit if already approved.
        if self.object.payment_request.status == "approved" or self.object.status == "approved":
            messages.info(request, "This payment is already approved and locked.")
            return redirect("payments:detail", pk=self.object.payment_request.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.status = "pending" # Reset to pending if it was rejected
        messages.success(self.request, "Payment confirmation updated and re-submitted.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("payments:detail", kwargs={"pk": self.object.payment_request.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_request"] = self.object.payment_request
        context["is_edit"] = True
        return context


from django.contrib.auth.decorators import login_required

@login_required
def approve_payment_confirmation(request, pk):
    """Owner approves the payment confirmation."""
    conf = get_object_or_404(PaymentConfirmation, pk=pk, payment_request__owner=request.user)
    
    if conf.status == "approved":
        messages.info(request, "This confirmation is already approved.")
        return redirect("payments:detail", pk=conf.payment_request.pk)

    conf.status = "approved"
    conf.reviewed_by = request.user
    conf.reviewed_at = timezone.now()
    conf.save() # This triggers handle_payment_approval in model.save()
    
    # Update the parent request status
    req = conf.payment_request
    req.status = "approved"
    req.save(update_fields=["status", "updated_at"])
    
    messages.success(request, f"Payment for '{req.title}' approved. Invoice has been generated.")
    return redirect("payments:detail", pk=req.pk)



class DownloadFinancialReportView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_owner:
            messages.error(request, "Only owners can access financial reports.")
            return redirect("core:dashboard")
            
        # Default to last 30 days if no dates provided
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=30)
        
        filename = f"financial_report_{user.id}_{end_date}.pdf"
        temp_path = Path(settings.MEDIA_ROOT) / "reports" / filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        generate_financial_statement(user, start_date, end_date, temp_path)
        
        return FileResponse(open(temp_path, "rb"), as_attachment=True, filename=filename)


@login_required
def reject_payment_confirmation(request, pk):
    """Owner rejects the payment confirmation."""
    conf = get_object_or_404(PaymentConfirmation, pk=pk, payment_request__owner=request.user)
    
    if conf.status == "rejected":
        messages.info(request, "This confirmation is already rejected.")
        return redirect("payments:detail", pk=conf.payment_request.pk)

    conf.status = "rejected"
    conf.reviewed_by = request.user
    conf.reviewed_at = timezone.now()
    conf.save()
    
    # Update the parent request status back to pending so tenant can try again?
    # Actually, if we reject, tenant might need to "re-submit". 
    # But the rule "Tenant can only Send 1 time" implies they should "Edit" instead of "Send new"?
    # User said: "After that he can Edit the Payment, but Can not change."
    # Wait, "Can not change"? Maybe they can edit the *Note* or *Proof* but not the request itself?
    # Let's keep it simple: if rejected, status goes back to pending so buttons reappear.
    req = conf.payment_request
    req.status = "pending" 
    req.save(update_fields=["status", "updated_at"])
    
    messages.warning(request, f"Payment for '{req.title}' rejected. Tenant notified.")
    return redirect("payments:detail", pk=req.pk)


from django.db.models import Sum

class FinancialDashboardView(LoginRequiredMixin, ListView):
    model = PaymentRequest
    template_name = "payments/finances.html"
    context_object_name = "approved_payments"

    def get_queryset(self):
        # Revenue = Approved Payment Requests
        return PaymentRequest.objects.filter(owner=self.request.user, status="approved")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Totals
        revenue = self.get_queryset().aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        
        expenses_qs = Expense.objects.filter(owner=user)
        expenses_total = expenses_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        
        context["revenue_total"] = revenue
        context["expenses_total"] = expenses_total
        context["net_profit"] = revenue - expenses_total
        context["expenses_list"] = expenses_qs[:10] # Recent 10
        
        # PDF generation link parameter (placeholder for now)
        context["report_date"] = timezone.now().date()
        
        return context


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from properties.models import Apartment
        apartments = Apartment.objects.filter(building__owner=self.request.user).values("id", "building_id", "apartment_name", "apartment_code")
        context["apartment_map"] = list(apartments)
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "payments/expense_form.html"
    success_url = reverse_lazy("payments:finances")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Expense added successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from properties.models import Apartment
        apartments = Apartment.objects.filter(building__owner=self.request.user).values("id", "building_id", "apartment_name", "apartment_code")
        context["apartment_map"] = list(apartments)
        return context
