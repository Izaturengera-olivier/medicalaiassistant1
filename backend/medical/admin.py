"""Admin registrations for medical. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import MedicalCondition


@admin.register(MedicalCondition)
class MedicalConditionAdmin(admin.ModelAdmin):
    """Admin interface for MedicalCondition."""

    list_display = ["name", "icd_code", "category", "created_at"]
    list_filter = ["category"]
    search_fields = ["name", "icd_code", "description"]
    readonly_fields = ["created_at", "updated_at"]
