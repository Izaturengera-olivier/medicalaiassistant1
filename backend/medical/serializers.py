"""DRF serializers for medical conditions."""

from rest_framework import serializers

from .models import MedicalCondition


class MedicalConditionSerializer(serializers.ModelSerializer):
    """Serializer for the MedicalCondition catalog."""

    class Meta:
        model = MedicalCondition
        fields = ["id", "name", "description", "icd_code", "category", "common_symptoms"]
        read_only_fields = ["id"]
