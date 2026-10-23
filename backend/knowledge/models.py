"""Domain models for knowledge. Implemented in Phase 2.

Approved sources, documents, chunks, embeddings.
"""

from django.db import models
from django.utils.text import slugify
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

    # Retrieval identifies sources by this stable key, so renaming the display
    # name in the admin must not orphan the documents attached to it.
    source_key = models.SlugField(
        _("source key"),
        max_length=60,
        blank=True,
        unique=True,
        help_text=_("Stable identifier used by retrieval, e.g. 'who'. Derived from the name when blank."),
    )
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

    def save(self, *args, **kwargs):
        if not self.source_key:
            self.source_key = _unique_slug(
                MedicalKnowledgeSource, "source_key", slugify(self.name)[:56] or "source", self.pk
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


def _unique_slug(model, field_name: str, base: str, pk=None) -> str:
    """Return `base`, suffixed with -2, -3... until no other row owns it.

    Keys are derived from human-readable text, so two documents with the same
    title would otherwise collide on insert.
    """
    candidate = base
    suffix = 1
    while model.objects.filter(**{field_name: candidate}).exclude(pk=pk).exists():
        suffix += 1
        candidate = f"{base[:58]}-{suffix}"
    return candidate


class KnowledgeDocument(models.Model):
    """A passage of approved clinical guidance that retrieval can hand to the model.

    Documents used to be Python literals inside the retrieval service, which meant
    nothing an admin approved could ever reach the AI.
    """

    source = models.ForeignKey(
        MedicalKnowledgeSource,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("source"),
    )
    document_key = models.SlugField(
        _("document key"),
        max_length=80,
        blank=True,
        unique=True,
        help_text=_("Stable identifier used for citations, e.g. 'doc_1'. Derived from the title when blank."),
    )
    title = models.CharField(_("title"), max_length=300)
    content = models.TextField(_("content"), help_text=_("Guidance text supplied to the model as evidence"))
    url = models.URLField(_("URL"), max_length=500, blank=True, help_text=_("Where this guidance was published"))
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Inactive documents are kept for audit but never retrieved"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "knowledge_documents"
        verbose_name = _("knowledge document")
        verbose_name_plural = _("knowledge documents")
        ordering = ["document_key"]

    def save(self, *args, **kwargs):
        if not self.document_key:
            self.document_key = _unique_slug(
                KnowledgeDocument, "document_key", slugify(self.title)[:72] or "doc", self.pk
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.source.name})"


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
