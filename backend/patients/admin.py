"""Admin registrations for patients. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import MedicalHistory


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MedicalHistory."""

    list_display = ["patient", "condition_name", "diagnosis_date", "treating_doctor"]
    list_filter = ["diagnosis_date"]
    search_fields = ["patient__email", "patient__first_name", "patient__last_name", "condition_name"]
    readonly_fields = ["created_at", "updated_at"]
