"""DRF serializers for knowledge. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import MedicalKnowledgeSource, RetrievedEvidence


class MedicalKnowledgeSourceSerializer(serializers.ModelSerializer):
    """Serializer for MedicalKnowledgeSource."""

    class Meta:
        model = MedicalKnowledgeSource
        fields = [
            "id", "name", "url", "source_type", "approval_status",
            "last_verified_date", "retrieval_config", "notes", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RetrievedEvidenceSerializer(serializers.ModelSerializer):
    """Serializer for RetrievedEvidence."""

    source = MedicalKnowledgeSourceSerializer(read_only=True)

    class Meta:
        model = RetrievedEvidence
        fields = [
            "id", "ai_assessment", "source", "title", "url",
            "publication_date", "retrieval_date", "relevance_score",
            "extracted_content", "key_points", "created_at"
        ]
        read_only_fields = ["id", "retrieval_date", "created_at"]


class KnowledgeSearchRequestSerializer(serializers.Serializer):
    """Serializer for knowledge search request."""

    query = serializers.CharField(help_text=_("Search query"))
    limit = serializers.IntegerField(default=8, help_text=_("Maximum number of results"))
    filter_approved = serializers.BooleanField(default=True, help_text=_("Filter by approved sources only"))


class KnowledgeSearchResponseSerializer(serializers.Serializer):
    """Serializer for knowledge search response."""

    query = serializers.CharField()
    results = serializers.ListField(child=serializers.DictField())
    total_results = serializers.IntegerField()
    sources_used = serializers.ListField(child=serializers.CharField())
