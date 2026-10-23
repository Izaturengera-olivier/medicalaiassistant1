"""Admin registrations for knowledge."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import KnowledgeDocument, MedicalKnowledgeSource, RetrievedEvidence


class KnowledgeDocumentInline(admin.TabularInline):
    model = KnowledgeDocument
    extra = 0
    fields = ["document_key", "title", "url", "is_active"]


@admin.register(MedicalKnowledgeSource)
class MedicalKnowledgeSourceAdmin(admin.ModelAdmin):
    """Admin interface for MedicalKnowledgeSource."""

    list_display = ["name", "source_key", "source_type", "approval_status", "last_verified_date", "document_count"]
    list_filter = ["source_type", "approval_status"]
    search_fields = ["name", "url", "source_key"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [KnowledgeDocumentInline]

    @admin.display(description=_("documents"))
    def document_count(self, obj):
        return obj.documents.count()


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    """Admin interface for the guidance passages the AI is allowed to cite."""

    list_display = ["title", "source", "document_key", "is_active", "updated_at"]
    list_filter = ["source", "is_active"]
    search_fields = ["title", "content", "document_key"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(RetrievedEvidence)
class RetrievedEvidenceAdmin(admin.ModelAdmin):
    """Admin interface for RetrievedEvidence."""

    list_display = ["ai_assessment", "source", "title", "relevance_score", "retrieval_date"]
    list_filter = ["source", "retrieval_date"]
    search_fields = ["title", "url"]
    readonly_fields = ["retrieval_date", "created_at"]
