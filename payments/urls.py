from __future__ import annotations

from django.urls import path

from .views import (
    DownloadFinancialReportView,
    ExpenseCreateView,
    FinancialDashboardView,
    PaymentConfirmationCreateView,
    PaymentConfirmationUpdateView,
    PaymentRequestCreateView,
    PaymentRequestDetailView,
    PaymentRequestListView,
    approve_payment_confirmation,
    reject_payment_confirmation,
)

app_name = "payments"

urlpatterns = [
    path("", PaymentRequestListView.as_view(), name="list"),
    path("create/", PaymentRequestCreateView.as_view(), name="create"),
    path("<int:pk>/", PaymentRequestDetailView.as_view(), name="detail"),
    path("<int:pk>/confirm/", PaymentConfirmationCreateView.as_view(), name="confirm"),
    path("confirmations/<int:pk>/edit/", PaymentConfirmationUpdateView.as_view(), name="edit_confirmation"),
    path("confirmations/<int:pk>/approve/", approve_payment_confirmation, name="approve_confirmation"),
    path("confirmations/<int:pk>/reject/", reject_payment_confirmation, name="reject_confirmation"),
    path("finances/", FinancialDashboardView.as_view(), name="finances"),
    path("finances/report/", DownloadFinancialReportView.as_view(), name="financial_report"),
    path("expenses/create/", ExpenseCreateView.as_view(), name="expense_create"),
]
