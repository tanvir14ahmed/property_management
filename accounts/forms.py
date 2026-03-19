from __future__ import annotations

from django import forms

from .models import IncompleteRegistration, User


class IncompleteSignUpForm(forms.ModelForm):
    class Meta:
        model = IncompleteRegistration
        fields = ["full_name", "email", "phone_number", "selected_role_intent"]

    def save(self, commit: bool = True) -> IncompleteRegistration:
        registration = super().save(commit=False)
        if commit:
            registration.save()
        return registration


class FinalizeSignUpForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords must match.")
        return password2


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "phone_number"]


class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(max_length=4, min_length=4, widget=forms.TextInput(attrs={
        'class': 'w-full rounded-xl border-slate-200 dark:border-slate-800 bg-transparent px-4 py-3 text-2xl font-black text-center tracking-[1em] focus:border-brand-500 focus:ring-brand-500',
        'placeholder': '0000',
        'autocomplete': 'one-time-code'
    }))
