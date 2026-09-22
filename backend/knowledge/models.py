"""Domain models for knowledge. Implemented in Phase 2.

Approved sources, documents, chunks, embeddings.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from ai.models import AIAssessment
from core.constants import SourceType


class MedicalKnowledgeSource(models.Model):
    """Approved medical knowledge sources for RAG."""

    APPROVAL_STATUS = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("deprecated", _("Deprecated")),
    ]

    name = models.CharField(_("source name"), max_length=200, unique=True)
    url = models.URLField(_("URL"), max_length=500, help_text=_("Source URL"))
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.CHOICES,
        verbose_name=_("source type")
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default="pending",
        verbose_name=_("approval status")
    )
    last_verified_date = models.DateField(
        _("last verified date"),
        null=True,
        blank=True,
        help_text=_("Date when source was last verified")
    )
    retrieval_config = models.JSONField(
        _("retrieval config"),
        default=dict,
        blank=True,
        help_text=_("Configuration for retrieval from this source")
    )
    notes = models.TextField(_("notes"), blank=True, help_text=_("Additional notes about the source"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_knowledge_sources"
        verbose_name = _("medical knowledge source")
        verbose_name_plural = _("medical knowledge sources")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class RetrievedEvidence(models.Model):
    """Evidence retrieved from medical knowledge sources."""

    ai_assessment = models.ForeignKey(
        AIAssessment,
        on_delete=models.CASCADE,
        related_name="retrieved_evidence",
        verbose_name=_("AI assessment")
    )
    source = models.ForeignKey(
        MedicalKnowledgeSource,
        on_delete=models.PROTECT,
        related_name="retrieved_evidence",
        verbose_name=_("source")
    )
    title = models.CharField(_("title"), max_length=500, help_text=_("Title of the retrieved document"))
    url = models.URLField(_("URL"), max_length=500, blank=True, help_text=_("URL of the source document"))
    publication_date = models.DateField(
        _("publication date"),
        null=True,
        blank=True,
        help_text=_("Date when the source was published")
    )
    retrieval_date = models.DateTimeField(_("retrieval date"), auto_now_add=True)
    relevance_score = models.FloatField(
        _("relevance score"),
        default=0.0,
        help_text=_("Score indicating relevance to the query")
    )
    extracted_content = models.TextField(
        _("extracted content"),
        help_text=_("Content extracted from the source")
    )
    key_points = models.JSONField(
        _("key points"),
        default=list,
        blank=True,
        help_text=_("Key points extracted from the content")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "retrieved_evidence"
        verbose_name = _("retrieved evidence")
        verbose_name_plural = _("retrieved evidence")
        ordering = ["-relevance_score", "-retrieval_date"]

    def __str__(self):
        return f"Evidence: {self.title[:50]}... (Score: {self.relevance_score})"
