"""Domain models for doctors. Implemented in Phase 2.

Doctor profiles and assigned-patient access.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from consultations.models import Consultation
from core.constants import AISuggestionAction


class DoctorReview(models.Model):
    """Doctor's review of AI assessment and consultation."""

    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="doctor_review",
        verbose_name=_("consultation")
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="doctor_reviews",
        limit_choices_to={"role": "DOCTOR"},
        verbose_name=_("doctor")
    )
    professional_diagnosis = models.TextField(
        _("professional diagnosis"),
        blank=True,
        help_text=_("Doctor's professional diagnosis")
    )
    clinical_notes = models.TextField(
        _("clinical notes"),
        blank=True,
        help_text=_("Additional clinical notes")
    )
    treatment_recommendations = models.TextField(
        _("treatment recommendations"),
        blank=True,
        help_text=_("Treatment recommendations by the doctor")
    )
    ai_suggestion_action = models.CharField(
        max_length=20,
        choices=AISuggestionAction.CHOICES,
        default=AISuggestionAction.ACCEPT,
        verbose_name=_("AI suggestion action")
    )
    modifications_made = models.JSONField(
        _("modifications made"),
        default=dict,
        blank=True,
        help_text=_("Details of modifications made to AI suggestions")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_reviews"
        verbose_name = _("doctor review")
        verbose_name_plural = _("doctor reviews")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Doctor Review for Consultation #{self.consultation.id}"
