"""Domain models for medical. Implemented in Phase 2.

Condition catalog and clinical reference entities.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class MedicalCondition(models.Model):
    """Catalog of medical conditions for reference."""

    CONDITION_CATEGORIES = [
        ("infectious", _("Infectious Disease")),
        ("chronic", _("Chronic Condition")),
        ("acute", _("Acute Condition")),
        ("genetic", _("Genetic Disorder")),
        ("mental_health", _("Mental Health")),
        ("other", _("Other")),
    ]

    name = models.CharField(_("condition name"), max_length=200, unique=True)
    description = models.TextField(_("description"), blank=True)
    icd_code = models.CharField(
        _("ICD code"),
        max_length=20,
        blank=True,
        help_text=_("International Classification of Diseases code")
    )
    category = models.CharField(
        max_length=20,
        choices=CONDITION_CATEGORIES,
        default="other",
        verbose_name=_("category")
    )
    common_symptoms = models.JSONField(
        _("common symptoms"),
        default=list,
        blank=True,
        help_text=_("List of common symptoms associated with this condition")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_conditions"
        verbose_name = _("medical condition")
        verbose_name_plural = _("medical conditions")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.icd_code or 'No ICD code'})"
