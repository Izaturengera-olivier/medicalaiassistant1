"""Domain models for pharmacists. Implemented in Phase 2.

Pharmacist profiles and prescription access.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from medications.models import Prescription


class PharmacistReview(models.Model):
    """Pharmacist's review of prescription for medication safety."""

    prescription = models.OneToOneField(
        Prescription,
        on_delete=models.CASCADE,
        related_name="pharmacist_review",
        verbose_name=_("prescription")
    )
    pharmacist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="pharmacist_reviews",
        limit_choices_to={"role": "PHARMACIST"},
        verbose_name=_("pharmacist")
    )
    notes = models.TextField(
        _("notes"),
        blank=True,
        help_text=_("Pharmacist's notes about the prescription")
    )
    interaction_flags = models.JSONField(
        _("interaction flags"),
        default=list,
        blank=True,
        help_text=_("Potential medication interactions detected")
    )
    allergy_flags = models.JSONField(
        _("allergy flags"),
        default=list,
        blank=True,
        help_text=_("Potential allergy issues detected")
    )
    recommendations = models.TextField(
        _("recommendations"),
        blank=True,
        help_text=_("Pharmacist's recommendations")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pharmacist_reviews"
        verbose_name = _("pharmacist review")
        verbose_name_plural = _("pharmacist reviews")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pharmacist Review for Prescription #{self.prescription.id}"
