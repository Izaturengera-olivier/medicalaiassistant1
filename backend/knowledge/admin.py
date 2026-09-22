"""Admin registrations for knowledge. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import MedicalKnowledgeSource, RetrievedEvidence


@admin.register(MedicalKnowledgeSource)
class MedicalKnowledgeSourceAdmin(admin.ModelAdmin):
    """Admin interface for MedicalKnowledgeSource."""

    list_display = ["name", "source_type", "approval_status", "last_verified_date"]
    list_filter = ["source_type", "approval_status"]
    search_fields = ["name", "url"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(RetrievedEvidence)
class RetrievedEvidenceAdmin(admin.ModelAdmin):
    """Admin interface for RetrievedEvidence."""

    list_display = ["ai_assessment", "source", "title", "relevance_score", "retrieval_date"]
    list_filter = ["source", "retrieval_date"]
    search_fields = ["title", "url"]
    readonly_fields = ["retrieval_date", "created_at"]
