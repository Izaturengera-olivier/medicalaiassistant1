"""DRF serializers for pharmacists. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from accounts.serializers import UserSerializer
from accounts.models import PharmacistProfile
from medications.models import Prescription, MedicationInteraction
from core.constants import PrescriptionStatus


class PharmacistProfileSerializer(serializers.ModelSerializer):
    """Serializer for PharmacistProfile."""
    
    user = UserSerializer(read_only=True)

    class Meta:
        model = PharmacistProfile
        fields = [
            "id", "user", "license_number", "pharmacy_name",
            "pharmacy_location", "verified", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for Prescription with medication details."""
    
    patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    doctor_name = serializers.CharField(source="prescribing_doctor.get_full_name", read_only=True)
    medication_name = serializers.CharField(source="medication.name", read_only=True)
    interactions = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            "id", "patient", "patient_name", "patient_email",
            "prescribing_doctor", "doctor_name", "medication", "medication_name",
            "dosage", "frequency", "duration", "instructions",
            "status", "prescribed_at", "interactions"
        ]
        read_only_fields = ["id", "prescribed_at"]

    def get_interactions(self, obj):
        """Get medication interactions for this prescription."""
        interactions = MedicationInteraction.objects.filter(
            medication_1=obj.medication
        )
        return [
            {
                "id": interaction.id,
                "interacting_medication": interaction.medication_2.name,
                "severity": interaction.severity,
                "description": interaction.description,
                "recommendation": interaction.recommendation
            }
            for interaction in interactions
        ]


class MedicationSafetyReviewSerializer(serializers.Serializer):
    """Serializer for medication safety review submission."""
    
    pharmacist_notes = serializers.CharField(required=False, allow_blank=True)
    interaction_flags = serializers.JSONField(required=False, default=list)
    review_status = serializers.ChoiceField(
        choices=[
            "APPROVED",
            "REJECTED",
            "FLAGGED"
        ]
    )


class PharmacistDashboardStatsSerializer(serializers.Serializer):
    """Serializer for pharmacist dashboard statistics."""
    
    total_prescriptions = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    approved_today = serializers.IntegerField()
    flagged_prescriptions = serializers.IntegerField()
