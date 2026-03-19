from __future__ import annotations

from django.urls import path

from . import views

app_name = "issues"

urlpatterns = [
    path("", views.IssueListView.as_view(), name="list"),
    path("create/", views.IssueCreateView.as_view(), name="create"),
    path("<int:pk>/resolve/", views.resolve_issue, name="resolve"),
    path("<int:pk>/approve/", views.approve_issue, name="approve"),
    path("<int:pk>/assign-vendor/", views.IssueAssignVendorView.as_view(), name="assign_vendor"),

    # Vendors
    path("vendors/", views.VendorListView.as_view(), name="vendor_list"),
    path("vendors/new/", views.VendorCreateView.as_view(), name="vendor_create"),
    path("vendors/<int:pk>/edit/", views.VendorUpdateView.as_view(), name="vendor_edit"),]
