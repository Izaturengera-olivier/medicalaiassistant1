"""DRF serializers for medications."""

from rest_framework import serializers

from .models import Medication, MedicationInteraction, Prescription


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for the Medication catalog."""

    class Meta:
        model = Medication
        fields = [
            "id", "name", "generic_name", "brand_names", "drug_class",
            "indications", "contraindications", "known_interactions",
            "allergy_warnings", "precautions", "reference_source",
            "last_verified_date",
        ]
        read_only_fields = ["id"]


class MedicationInteractionSerializer(serializers.ModelSerializer):
    """Serializer for documented medication interactions."""

    medication_1_name = serializers.CharField(source="medication_1.name", read_only=True)
    medication_2_name = serializers.CharField(source="medication_2.name", read_only=True)

    class Meta:
        model = MedicationInteraction
        fields = [
            "id", "medication_1", "medication_1_name",
            "medication_2", "medication_2_name",
            "interaction_type", "severity", "description",
            "evidence_source", "recommendation",
        ]
        read_only_fields = ["id"]


class PrescriptionReferenceSerializer(serializers.ModelSerializer):
    """Read-only prescription summary for catalog cross-references."""

    patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)
    medication_name = serializers.CharField(source="medication.name", read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id", "patient", "patient_name", "medication", "medication_name",
            "dosage", "frequency", "duration", "status", "prescribed_at",
        ]
        read_only_fields = fields
