from __future__ import annotations

from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import FinalizeSignUpForm, IncompleteSignUpForm, ProfileForm
from .models import IncompleteRegistration


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .forms import FinalizeSignUpForm, IncompleteSignUpForm, ProfileForm, OTPVerifyForm


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = IncompleteSignUpForm

    def form_valid(self, form):
        registration = form.save()
        
        # Generate 4-digit OTP
        otp = f"{random.randint(1000, 9999)}"
        registration.otp_code = otp
        registration.otp_expiry = timezone.now() + timedelta(minutes=10)
        registration.save()
        
        # Send professional email
        subject = "Verify Your Property Suite Account"
        message = f"""
Dear {registration.full_name},

Thank you for choosing Property Suite. To complete your registration, please use the following 4-digit verification code:

Verification Code: {otp}

This code will expire in 10 minutes. If you did not request this, please ignore this email.

Best regards,
The Property Suite Team
        """
        html_message = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px;">
            <h2 style="color: #0284c7; margin-bottom: 20px;">Welcome to Property Suite</h2>
            <p>Verification code for completing your registration:</p>
            <div style="background: #f1f5f9; padding: 20px; border-radius: 8px; text-align: center; margin: 24px 0;">
                <span style="font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #0f172a;">{otp}</span>
            </div>
            <p style="color: #64748b; font-size: 14px;">This code will expire in 10 minutes.</p>
            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;">
            <p style="color: #94a3b8; font-size: 12px;">If you did not initiate this request, please contact support.</p>
        </div>
        """
        
        try:
            send_mail(
                subject,
                message,
                from_email=None,  # Uses DEFAULT_FROM_EMAIL
                recipient_list=[registration.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # For development, you might want to log this or show a warning
            print(f"SMTP ERROR: {e}")
            messages.warning(self.request, f"Could not send verification email: {e}")
        
        return redirect("accounts:verify_otp", pk=registration.pk)


class VerifyOTPView(FormView):
    template_name = "accounts/verify_otp.html"
    form_class = OTPVerifyForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration"] = get_object_or_404(IncompleteRegistration, pk=self.kwargs["pk"], is_completed=False)
        return context

    def form_valid(self, form):
        registration = get_object_or_404(IncompleteRegistration, pk=self.kwargs["pk"], is_completed=False)
        entered_otp = form.cleaned_data["otp_code"]
        
        if registration.otp_code == entered_otp and registration.otp_expiry > timezone.now():
            registration.is_otp_verified = True
            registration.save()
            return redirect("accounts:complete_signup", pk=registration.pk)
        else:
            messages.error(self.request, "Invalid or expired verification code.")
            return self.form_invalid(form)


class FinalizeRegistrationView(FormView):
    template_name = "accounts/complete_signup.html"
    form_class = FinalizeSignUpForm
    success_url = reverse_lazy("core:dashboard")

    def dispatch(self, request, *args, **kwargs):
        registration = get_object_or_404(IncompleteRegistration, pk=kwargs["pk"], is_completed=False)
        if not registration.is_otp_verified:
            messages.warning(request, "Please verify your email first.")
            return redirect("accounts:verify_otp", pk=registration.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["registration"] = get_object_or_404(IncompleteRegistration, pk=self.kwargs["pk"], is_completed=False)
        return context

    def form_valid(self, form):
        registration = get_object_or_404(IncompleteRegistration, pk=self.kwargs["pk"], is_completed=False)
        email = registration.email
        
        from .models import User
        if User.objects.filter(email=email).exists():
            messages.error(self.request, "An account with this email already exists.")
            return self.form_invalid(form)

        user = User.objects.create_user(
            email=email,
            full_name=registration.full_name,
            phone_number=registration.phone_number,
            password=form.cleaned_data["password1"]
        )
        
        intent = registration.selected_role_intent
        user.is_owner = intent in {1, 3}
        user.is_tenant = intent in {2, 3}
        user.save()

        registration.mark_completed()
        login(self.request, user)
        messages.success(self.request, f"Welcome to Property Suite, {user.full_name}!")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "accounts/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)
