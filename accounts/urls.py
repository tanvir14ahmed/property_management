from __future__ import annotations

from django.urls import include, path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("signup/verify/<int:pk>/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("signup/complete/<int:pk>/", views.FinalizeRegistrationView.as_view(), name="complete_signup"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
]
