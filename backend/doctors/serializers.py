"""DRF serializers for doctors. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from accounts.serializers import UserSerializer
from accounts.models import DoctorProfile
from consultations.models import Consultation
from ai.models import AIAssessment


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for DoctorProfile."""
    
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id", "user", "license_number", "specialization",
            "hospital_or_clinic", "years_of_experience", "verified",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class PatientConsultationSerializer(serializers.ModelSerializer):
    """Serializer for patient consultations from doctor's perspective."""
    
    patient_name = serializers.CharField(source="patient.get_full_name", read_only=True)
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    ai_assessment = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = [
            "id", "patient", "patient_name", "patient_email",
            "chief_complaint", "status", "assigned_doctor",
            "created_at", "updated_at", "ai_assessment"
        ]
        read_only_fields = ["id", "patient", "created_at", "updated_at"]

    def get_ai_assessment(self, obj):
        """Get AI assessment if available."""
        try:
            assessment = obj.ai_assessments.first()
            if assessment:
                return {
                    "id": assessment.id,
                    "symptoms_identified": assessment.symptoms_identified,
                    "possible_conditions": assessment.possible_conditions_list,
                    "urgency_level": assessment.urgency_level,
                    "warning_signs": assessment.warning_signs,
                    "recommended_next_step": assessment.recommended_next_step,
                    "created_at": assessment.created_at
                }
        except:
            pass
        return None


class ConsultationReviewSerializer(serializers.Serializer):
    """Serializer for consultation review submission."""
    
    consultation_id = serializers.IntegerField()
    diagnosis = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    treatment_recommendation = serializers.CharField(required=False, allow_blank=True)
    follow_up_required = serializers.BooleanField(default=False)
    status = serializers.ChoiceField(
        choices=[
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED"
        ]
    )
    accept_ai_assessment = serializers.BooleanField(default=False)


class DoctorDashboardStatsSerializer(serializers.Serializer):
    """Serializer for doctor dashboard statistics."""
    
    total_patients = serializers.IntegerField()
    active_consultations = serializers.IntegerField()
    completed_consultations = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    urgent_cases = serializers.IntegerField()
