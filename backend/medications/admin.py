"""Admin registrations for medications. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Medication, MedicationInteraction, Prescription, PrescriptionMedication


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    """Admin interface for Medication."""

    list_display = ["name", "generic_name", "drug_class", "last_verified_date"]
    list_filter = ["drug_class"]
    search_fields = ["name", "generic_name", "brand_names"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(MedicationInteraction)
class MedicationInteractionAdmin(admin.ModelAdmin):
    """Admin interface for MedicationInteraction."""

    list_display = ["medication_1", "medication_2", "interaction_type", "severity"]
    list_filter = ["interaction_type", "severity"]
    search_fields = ["medication_1__name", "medication_2__name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """Admin interface for Prescription."""

    list_display = ["id", "consultation", "prescribing_doctor", "status", "prescribed_date"]
    list_filter = ["status", "prescribed_date"]
    search_fields = ["consultation__patient__email", "prescribing_doctor__email"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PrescriptionMedication)
class PrescriptionMedicationAdmin(admin.ModelAdmin):
    """Admin interface for PrescriptionMedication."""

    list_display = ["prescription", "medication", "dosage", "frequency"]
    search_fields = ["medication__name", "prescription__id"]
    readonly_fields = ["created_at"]
