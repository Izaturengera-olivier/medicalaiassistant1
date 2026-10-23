from django.contrib import admin
from django.urls import include, path

from config.health import HealthView
from config.system_views import get_system_settings, update_system_settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/admin/settings/", get_system_settings, name="get_system_settings"),
    path("api/admin/settings/update/", update_system_settings, name="update_system_settings"),
    path("api/schema/", include("config.schema_urls")),
    path("api/auth/", include("accounts.urls")),
    path("api/consultations/", include("consultations.urls")),
    path("api/patients/", include("patients.urls")),
    path("api/doctors/", include("doctors.urls")),
    path("api/pharmacists/", include("pharmacists.urls")),
    path("api/medical/", include("medical.urls")),
    path("api/medications/", include("medications.urls")),
    path("api/ai/", include("ai.urls")),
    path("api/knowledge/", include("knowledge.urls")),
    path("api/audit/", include("audit.urls")),
]

import os
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif os.environ.get("SERVE_MEDIA_LOCAL", "true").lower() == "true":
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]

