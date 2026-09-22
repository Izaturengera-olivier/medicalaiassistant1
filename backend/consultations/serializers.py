"""DRF serializers for consultations. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Consultation, Symptom, PatientSymptom, FollowUpQuestion
from accounts.serializers import UserSerializer


class SymptomSerializer(serializers.ModelSerializer):
    """Serializer for Symptom model."""

    class Meta:
        model = Symptom
        fields = ["id", "name", "description", "category", "severity_levels"]
        read_only_fields = ["id"]


class PatientSymptomSerializer(serializers.ModelSerializer):
    """Serializer for PatientSymptom model."""

    symptom = SymptomSerializer(read_only=True)
    symptom_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PatientSymptom
        fields = ["id", "consultation", "symptom", "symptom_id", "severity", "duration", "notes", "reported_at"]
        read_only_fields = ["id", "reported_at"]


class FollowUpQuestionSerializer(serializers.ModelSerializer):
    """Serializer for FollowUpQuestion model."""

    class Meta:
        model = FollowUpQuestion
        fields = ["id", "consultation", "question", "answer", "asked_at", "answered_at"]
        read_only_fields = ["id", "asked_at", "answered_at"]


class ConsultationSerializer(serializers.ModelSerializer):
    """Serializer for Consultation model."""

    patient = UserSerializer(read_only=True)
    assigned_doctor = UserSerializer(read_only=True)
    patient_symptoms = PatientSymptomSerializer(many=True, read_only=True)
    follow_up_questions = FollowUpQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Consultation
        fields = [
            "id", "patient", "assigned_doctor", "status", "chief_complaint",
            "patient_symptoms", "follow_up_questions", "created_at", "updated_at", "completed_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "completed_at"]


class ConsultationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new consultation."""

    class Meta:
        model = Consultation
        fields = ["chief_complaint"]

    def create(self, validated_data):
        validated_data["patient"] = self.context["request"].user
        validated_data["status"] = "IN_PROGRESS"
        return super().create(validated_data)


class ConsultationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating consultation status."""

    assigned_doctor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Consultation
        fields = ["status", "assigned_doctor_id"]

    def update(self, instance, validated_data):
        assigned_doctor_id = validated_data.pop("assigned_doctor_id", None)
        if assigned_doctor_id is not None:
            from accounts.models import User
            try:
                assigned_doctor = User.objects.get(id=assigned_doctor_id, role="DOCTOR")
                instance.assigned_doctor = assigned_doctor
            except User.DoesNotExist:
                raise serializers.ValidationError({"assigned_doctor_id": _("Invalid doctor ID")})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
