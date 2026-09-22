"""Domain models for patients. Implemented in Phase 2.

Patient profiles and medical history.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class MedicalHistory(models.Model):
    """Medical history for patients."""

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medical_history",
        limit_choices_to={"role": "PATIENT"},
        verbose_name=_("patient")
    )
    condition_name = models.CharField(
        _("condition name"),
        max_length=200,
        help_text=_("Name of the medical condition")
    )
    diagnosis_date = models.DateField(
        _("diagnosis date"),
        null=True,
        blank=True,
        help_text=_("Date when condition was diagnosed")
    )
    treating_doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="treated_patients",
        limit_choices_to={"role": "DOCTOR"},
        verbose_name=_("treating doctor")
    )
    notes = models.TextField(_("notes"), blank=True, help_text=_("Additional notes about the condition"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_history"
        verbose_name = _("medical history")
        verbose_name_plural = _("medical histories")
        ordering = ["-diagnosis_date", "-created_at"]

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.condition_name}"
