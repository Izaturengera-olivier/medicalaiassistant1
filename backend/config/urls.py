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

