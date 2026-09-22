"""Admin registrations for ai. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AIAssessment, PossibleCondition


@admin.register(AIAssessment)
class AIAssessmentAdmin(admin.ModelAdmin):
    """Admin interface for AIAssessment."""

    list_display = ["id", "consultation", "urgency_level", "model_used", "created_at"]
    list_filter = ["urgency_level", "created_at"]
    search_fields = ["consultation__patient__email", "model_used"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PossibleCondition)
class PossibleConditionAdmin(admin.ModelAdmin):
    """Admin interface for PossibleCondition."""

    list_display = ["ai_assessment", "condition_name", "likelihood", "confidence_level"]
    list_filter = ["likelihood", "confidence_level"]
    search_fields = ["condition_name", "reasoning"]
    readonly_fields = ["created_at"]
