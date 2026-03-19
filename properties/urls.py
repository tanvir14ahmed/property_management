from __future__ import annotations

from django.urls import path

from . import views

app_name = "properties"

urlpatterns = [
    # Public Listings
    path("listings/", views.PublicListingView.as_view(), name="public_listings"),
    
    # Buildings
    path("buildings/", views.BuildingListView.as_view(), name="building_list"),
    path("buildings/new/", views.BuildingCreateView.as_view(), name="building_create"),
    path("buildings/<int:pk>/", views.BuildingDetailView.as_view(), name="building_detail"),
    path("buildings/<int:pk>/edit/", views.BuildingUpdateView.as_view(), name="building_edit"),

    # Apartments
    path("buildings/<int:building_pk>/apartments/new/", views.ApartmentCreateView.as_view(), name="apartment_create"),
    path("apartments/<int:pk>/", views.ApartmentDetailView.as_view(), name="apartment_detail"),
    path("apartments/<int:pk>/edit/", views.ApartmentUpdateView.as_view(), name="apartment_edit"),
    path("occupancies/<int:pk>/upload-lease/", views.UploadLeaseView.as_view(), name="upload_lease"),

    # Join Requests (Owner side)
    path("join-requests/", views.JoinRequestListView.as_view(), name="join_request_list"),
    path("join-requests/<int:pk>/approve/", views.approve_join_request, name="join_request_approve"),
    path("join-requests/<int:pk>/reject/", views.reject_join_request, name="join_request_reject"),

    # Search & Request (Tenant side)
    path("search/", views.ApartmentSearchView.as_view(), name="search"),
    path("apartments/<int:apartment_pk>/request-join/", views.submit_join_request, name="submit_join_request"),
]
