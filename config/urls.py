from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("properties/", include("properties.urls", namespace="properties")),
    path("payments/", include("payments.urls", namespace="payments")),
    path("issues/", include("issues.urls", namespace="issues")),
    path("chat/", include("chatapp.urls", namespace="chatapp")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("", include("core.urls", namespace="core")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
