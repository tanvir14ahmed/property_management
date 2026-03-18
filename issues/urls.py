from __future__ import annotations

from django.urls import path

from . import views

app_name = "issues"

urlpatterns = [
    path("", views.IssueListView.as_view(), name="list"),
    path("create/", views.IssueCreateView.as_view(), name="create"),
    path("<int:pk>/resolve/", views.resolve_issue, name="resolve"),
    path("<int:pk>/approve/", views.approve_issue, name="approve"),
]
