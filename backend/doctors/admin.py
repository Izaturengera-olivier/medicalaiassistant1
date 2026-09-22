"""Admin registrations for doctors. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import DoctorReview


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    """Admin interface for DoctorReview."""

    list_display = ["consultation", "doctor", "ai_suggestion_action", "created_at"]
    list_filter = ["ai_suggestion_action", "created_at"]
    search_fields = ["consultation__patient__email", "doctor__email"]
    readonly_fields = ["created_at", "updated_at"]
