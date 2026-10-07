"""Domain models for ai. Implemented in Phase 2.

LLM interfaces, structured assessment, triage.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from consultations.models import Consultation
from core.constants import UrgencyLevel


class ChatConversation(models.Model):
    """A saved chat thread so users can reopen previous conversations."""

    KIND_CHOICES = [
        ("patient", _("Patient symptom chat")),
        ("professional", _("Professional assistant chat")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_conversations",
        verbose_name=_("user")
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="patient")
    title = models.CharField(_("title"), max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chat_conversations"
        verbose_name = _("chat conversation")
        verbose_name_plural = _("chat conversations")
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Conversation #{self.id}"


class ChatMessage(models.Model):
    """A single message in a saved chat conversation."""

    ROLE_CHOICES = [
        ("user", _("User")),
        ("assistant", _("Assistant")),
    ]

    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("conversation")
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(_("content"))
    details = models.JSONField(_("details"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
        verbose_name = _("chat message")
        verbose_name_plural = _("chat messages")
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"


class AIAssessment(models.Model):
    """Structured AI assessment for a consultation."""

    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="ai_assessment",
        verbose_name=_("consultation")
    )
    symptoms_identified = models.JSONField(
        _("symptoms identified"),
        default=list,
        blank=True,
        help_text=_("List of symptoms identified by AI")
    )
    follow_up_questions = models.JSONField(
        _("follow-up questions"),
        default=list,
        blank=True,
        help_text=_("Generated follow-up questions")
    )
    possible_conditions_list = models.JSONField(
        _("possible conditions list"),
        default=list,
        blank=True,
        help_text=_("List of possible conditions identified")
    )
    warning_signs = models.JSONField(
        _("warning signs"),
        default=list,
        blank=True,
        help_text=_("Emergency or warning signs detected")
    )
    urgency_level = models.CharField(
        max_length=30,
        choices=UrgencyLevel.CHOICES,
        default=UrgencyLevel.INFORMATIONAL,
        verbose_name=_("urgency level")
    )
    general_information = models.TextField(
        _("general information"),
        blank=True,
        help_text=_("General medical information for the patient")
    )
    medication_information = models.JSONField(
        _("medication information"),
        default=list,
        blank=True,
        help_text=_("Medication-related information")
    )
    recommended_next_step = models.TextField(
        _("recommended next step"),
        blank=True,
        help_text=_("Recommended action for the patient")
    )
    sources = models.JSONField(
        _("sources"),
        default=list,
        blank=True,
        help_text=_("Sources used for the assessment")
    )
    model_used = models.CharField(
        _("model used"),
        max_length=100,
        blank=True,
        help_text=_("AI model used for assessment")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_assessments"
        verbose_name = _("AI assessment")
        verbose_name_plural = _("AI assessments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"AI Assessment for Consultation #{self.consultation.id}"


class PossibleCondition(models.Model):
    """Possible condition identified by AI assessment."""

    CONFIDENCE_LEVELS = [
        ("low", _("Low")),
        ("medium", _("Medium")),
        ("high", _("High")),
    ]

    ai_assessment = models.ForeignKey(
        AIAssessment,
        on_delete=models.CASCADE,
        related_name="identified_conditions",
        verbose_name=_("AI assessment")
    )
    condition_name = models.CharField(
        _("condition name"),
        max_length=200,
        help_text=_("Name of the possible condition")
    )
    likelihood = models.CharField(
        max_length=20,
        choices=CONFIDENCE_LEVELS,
        default="low",
        verbose_name=_("likelihood")
    )
    confidence_level = models.CharField(
        max_length=20,
        choices=CONFIDENCE_LEVELS,
        default="low",
        verbose_name=_("confidence level")
    )
    reasoning = models.TextField(
        _("reasoning"),
        blank=True,
        help_text=_("AI reasoning for this condition")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "possible_conditions"
        verbose_name = _("possible condition")
        verbose_name_plural = _("possible conditions")
        ordering = ["-confidence_level", "condition_name"]

    def __str__(self):
        return f"{self.condition_name} ({self.likelihood})"
