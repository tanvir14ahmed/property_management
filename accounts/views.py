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


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = IncompleteSignUpForm

    def form_valid(self, form):
        registration = form.save()
        return redirect("accounts:complete_signup", pk=registration.pk)


class FinalizeRegistrationView(FormView):
    template_name = "accounts/complete_signup.html"
    form_class = FinalizeSignUpForm
    success_url = reverse_lazy("core:dashboard")

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
