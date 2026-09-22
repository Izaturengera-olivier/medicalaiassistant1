"""Admin registrations for consultations. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Consultation, Symptom, PatientSymptom, FollowUpQuestion


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """Admin interface for Consultation."""

    list_display = ["id", "patient", "assigned_doctor", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["patient__email", "patient__first_name", "patient__last_name", "chief_complaint"]
    readonly_fields = ["created_at", "updated_at", "completed_at"]


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    """Admin interface for Symptom."""

    list_display = ["name", "category", "created_at"]
    list_filter = ["category"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PatientSymptom)
class PatientSymptomAdmin(admin.ModelAdmin):
    """Admin interface for PatientSymptom."""

    list_display = ["consultation", "symptom", "severity", "duration", "reported_at"]
    list_filter = ["severity", "reported_at"]
    search_fields = ["symptom__name", "consultation__patient__email"]
    readonly_fields = ["reported_at"]


@admin.register(FollowUpQuestion)
class FollowUpQuestionAdmin(admin.ModelAdmin):
    """Admin interface for FollowUpQuestion."""

    list_display = ["consultation", "question", "asked_at", "answered_at"]
    search_fields = ["question", "answer"]
    readonly_fields = ["asked_at", "answered_at"]
