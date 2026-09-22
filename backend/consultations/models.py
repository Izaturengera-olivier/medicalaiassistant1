"""Domain models for consultations. Implemented in Phase 2.

Consultations, symptoms, follow-up questions.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from core.constants import ConsultationStatus


class Consultation(models.Model):
    """Patient consultation for symptom assessment."""

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="consultations",
        limit_choices_to={"role": "PATIENT"},
        verbose_name=_("patient")
    )
    assigned_doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_consultations",
        limit_choices_to={"role": "DOCTOR"},
        verbose_name=_("assigned doctor")
    )
    status = models.CharField(
        max_length=20,
        choices=ConsultationStatus.CHOICES,
        default=ConsultationStatus.IN_PROGRESS,
        verbose_name=_("status")
    )
    chief_complaint = models.TextField(
        _("chief complaint"),
        help_text=_("Primary reason for consultation")
    )
    doctor_notes = models.TextField(_("doctor notes"), blank=True)
    diagnosis = models.TextField(_("diagnosis"), blank=True)
    treatment_recommendation = models.TextField(_("treatment recommendation"), blank=True)
    follow_up_required = models.BooleanField(_("follow-up required"), default=False)
    ai_assessment_accepted = models.BooleanField(_("AI assessment accepted"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "consultations"
        verbose_name = _("consultation")
        verbose_name_plural = _("consultations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Consultation #{self.id} - {self.patient.get_full_name()}"


class Symptom(models.Model):
    """Catalog of symptoms for reference."""

    SEVERITY_LEVELS = [
        ("mild", _("Mild")),
        ("moderate", _("Moderate")),
        ("severe", _("Severe")),
    ]

    name = models.CharField(_("symptom name"), max_length=200, unique=True)
    description = models.TextField(_("description"), blank=True)
    category = models.CharField(
        _("category"),
        max_length=100,
        blank=True,
        help_text=_("e.g., respiratory, gastrointestinal, neurological")
    )
    severity_levels = models.JSONField(
        _("severity levels"),
        default=list,
        blank=True,
        help_text=_("Available severity levels for this symptom")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "symptoms"
        verbose_name = _("symptom")
        verbose_name_plural = _("symptoms")
        ordering = ["name"]

    def __str__(self):
        return self.name


class PatientSymptom(models.Model):
    """Symptoms reported by a patient in a consultation."""

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="patient_symptoms",
        verbose_name=_("consultation")
    )
    symptom = models.ForeignKey(
        Symptom,
        on_delete=models.PROTECT,
        related_name="patient_reports",
        verbose_name=_("symptom")
    )
    severity = models.CharField(
        max_length=20,
        choices=Symptom.SEVERITY_LEVELS,
        default="moderate",
        verbose_name=_("severity")
    )
    duration = models.CharField(
        _("duration"),
        max_length=100,
        blank=True,
        help_text=_("e.g., '2 days', '1 week', '3 hours'")
    )
    notes = models.TextField(_("notes"), blank=True, help_text=_("Additional details about the symptom"))
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patient_symptoms"
        verbose_name = _("patient symptom")
        verbose_name_plural = _("patient symptoms")
        ordering = ["-reported_at"]

    def __str__(self):
        return f"{self.symptom.name} ({self.severity}) - Consultation #{self.consultation.id}"


class FollowUpQuestion(models.Model):
    """Follow-up questions asked during consultation."""

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name="follow_up_questions",
        verbose_name=_("consultation")
    )
    question = models.TextField(_("question"), help_text=_("The follow-up question asked"))
    answer = models.TextField(_("answer"), blank=True, help_text=_("Patient's answer to the question"))
    asked_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "follow_up_questions"
        verbose_name = _("follow-up question")
        verbose_name_plural = _("follow-up questions")
        ordering = ["asked_at"]

    def __str__(self):
        return f"Question for Consultation #{self.consultation.id}: {self.question[:50]}..."
