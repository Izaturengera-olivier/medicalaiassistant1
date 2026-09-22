"""Domain models for medications. Implemented in Phase 2.

Medication catalog, interactions, prescriptions.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from consultations.models import Consultation
from core.constants import PrescriptionStatus


class Medication(models.Model):
    """Catalog of medications for reference."""

    DRUG_CLASSES = [
        ("antibiotic", _("Antibiotic")),
        ("analgesic", _("Analgesic")),
        ("antihypertensive", _("Antihypertensive")),
        ("antidiabetic", _("Antidiabetic")),
        ("antidepressant", _("Antidepressant")),
        ("anticoagulant", _("Anticoagulant")),
        ("antiinflammatory", _("Anti-inflammatory")),
        ("other", _("Other")),
    ]

    name = models.CharField(_("medication name"), max_length=200, unique=True)
    generic_name = models.CharField(_("generic name"), max_length=200, blank=True)
    brand_names = models.JSONField(
        _("brand names"),
        default=list,
        blank=True,
        help_text=_("List of brand names")
    )
    drug_class = models.CharField(
        max_length=20,
        choices=DRUG_CLASSES,
        default="other",
        verbose_name=_("drug class")
    )
    indications = models.JSONField(
        _("indications"),
        default=list,
        blank=True,
        help_text=_("Approved uses/indications")
    )
    contraindications = models.JSONField(
        _("contraindications"),
        default=list,
        blank=True,
        help_text=_("Contraindications and warnings")
    )
    known_interactions = models.JSONField(
        _("known interactions"),
        default=list,
        blank=True,
        help_text=_("Known drug-drug interactions")
    )
    allergy_warnings = models.JSONField(
        _("allergy warnings"),
        default=list,
        blank=True,
        help_text=_("Allergy-related warnings")
    )
    precautions = models.JSONField(
        _("precautions"),
        default=list,
        blank=True,
        help_text=_("Important precautions")
    )
    reference_source = models.CharField(
        _("reference source"),
        max_length=300,
        blank=True,
        help_text=_("Source of medication information")
    )
    last_verified_date = models.DateField(
        _("last verified date"),
        null=True,
        blank=True,
        help_text=_("Date when medication information was last verified")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medications"
        verbose_name = _("medication")
        verbose_name_plural = _("medications")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.generic_name or 'No generic name'})"


class MedicationInteraction(models.Model):
    """Documented medication interactions."""

    INTERACTION_TYPES = [
        ("pharmacokinetic", _("Pharmacokinetic")),
        ("pharmacodynamic", _("Pharmacodynamic")),
        ("contraindicated", _("Contraindicated")),
        ("caution", _("Use with Caution")),
    ]

    SEVERITY_LEVELS = [
        ("mild", _("Mild")),
        ("moderate", _("Moderate")),
        ("severe", _("Severe")),
        ("contraindicated", _("Contraindicated")),
    ]

    medication_1 = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="interactions_as_med1",
        verbose_name=_("medication 1")
    )
    medication_2 = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="interactions_as_med2",
        verbose_name=_("medication 2")
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES,
        verbose_name=_("interaction type")
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        verbose_name=_("severity")
    )
    description = models.TextField(_("description"), help_text=_("Description of the interaction"))
    evidence_source = models.CharField(
        _("evidence source"),
        max_length=300,
        blank=True,
        help_text=_("Source of interaction information")
    )
    recommendation = models.TextField(
        _("recommendation"),
        blank=True,
        help_text=_("Clinical recommendation for managing the interaction")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medication_interactions"
        verbose_name = _("medication interaction")
        verbose_name_plural = _("medication interactions")
        unique_together = ["medication_1", "medication_2"]
        ordering = ["-severity", "medication_1", "medication_2"]

    def __str__(self):
        return f"Interaction: {self.medication_1.name} + {self.medication_2.name} ({self.severity})"


class Prescription(models.Model):
    """Prescription for a patient consultation."""

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="prescriptions",
        verbose_name=_("consultation")
    )
    prescribing_doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="prescribed_medications",
        limit_choices_to={"role": "DOCTOR"},
        verbose_name=_("prescribing doctor")
    )
    prescribed_date = models.DateField(_("prescribed date"), auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=PrescriptionStatus.CHOICES,
        default=PrescriptionStatus.ACTIVE,
        verbose_name=_("status")
    )
    notes = models.TextField(_("notes"), blank=True, help_text=_("Additional prescription notes"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "prescriptions"
        verbose_name = _("prescription")
        verbose_name_plural = _("prescriptions")
        ordering = ["-prescribed_date"]

    def __str__(self):
        return f"Prescription #{self.id} - Consultation #{self.consultation.id}"


class PrescriptionMedication(models.Model):
    """Individual medications within a prescription."""

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="medications",
        verbose_name=_("prescription")
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        related_name="prescription_items",
        verbose_name=_("medication")
    )
    dosage = models.CharField(
        _("dosage"),
        max_length=100,
        help_text=_("e.g., '500mg', '10mg', '1 tablet'")
    )
    frequency = models.CharField(
        _("frequency"),
        max_length=100,
        help_text=_("e.g., 'twice daily', 'every 8 hours', 'once daily'")
    )
    duration = models.CharField(
        _("duration"),
        max_length=100,
        help_text=_("e.g., '7 days', '2 weeks', '30 days'")
    )
    instructions = models.TextField(
        _("instructions"),
        blank=True,
        help_text=_("Specific instructions for taking this medication")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "prescription_medications"
        verbose_name = _("prescription medication")
        verbose_name_plural = _("prescription medications")
        ordering = ["prescription", "id"]

    def __str__(self):
        return f"{self.medication.name} - {self.dosage}, {self.frequency}"
