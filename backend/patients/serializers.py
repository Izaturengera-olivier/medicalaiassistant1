"""DRF serializers for patients. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import MedicalHistory
from accounts.models import User
from accounts.serializers import UserSerializer


class MedicalHistorySerializer(serializers.ModelSerializer):
    """Serializer for MedicalHistory model."""

    patient = UserSerializer(read_only=True)
    treating_doctor = UserSerializer(read_only=True)

    class Meta:
        model = MedicalHistory
        fields = [
            "id", "patient", "condition_name", "diagnosis_date",
            "treating_doctor", "notes", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MedicalHistoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating medical history."""

    treating_doctor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = MedicalHistory
        fields = ["condition_name", "diagnosis_date", "treating_doctor_id", "notes"]

    def create(self, validated_data):
        validated_data["patient"] = self.context["request"].user
        treating_doctor_id = validated_data.pop("treating_doctor_id", None)
        if treating_doctor_id:
            try:
                validated_data["treating_doctor"] = User.objects.get(id=treating_doctor_id, role="DOCTOR")
            except User.DoesNotExist:
                raise serializers.ValidationError({"treating_doctor_id": _("Invalid doctor ID")})
        return super().create(validated_data)
