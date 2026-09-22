"""DRF serializers for ai. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import AIAssessment, PossibleCondition


class PossibleConditionSerializer(serializers.ModelSerializer):
    """Serializer for PossibleCondition."""

    class Meta:
        model = PossibleCondition
        fields = ["id", "condition_name", "likelihood", "confidence_level", "reasoning"]
        read_only_fields = ["id"]


class AIAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for AIAssessment."""

    possible_conditions = PossibleConditionSerializer(many=True, read_only=True)

    class Meta:
        model = AIAssessment
        fields = [
            "id", "consultation", "symptoms_identified", "follow_up_questions",
            "possible_conditions_list", "warning_signs", "urgency_level",
            "general_information", "medication_information", "recommended_next_step",
            "sources", "model_used", "possible_conditions", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "consultation"]


class AIAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for AI analysis request."""

    patient_input = serializers.CharField(
        help_text=_("Patient's description of symptoms")
    )
    patient_history = serializers.JSONField(
        required=False,
        help_text=_("Patient's medical history")
    )
    current_medications = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text=_("List of current medications")
    )


class AIAnalysisResponseSerializer(serializers.Serializer):
    """Serializer for AI analysis response."""

    symptoms_identified = serializers.ListField(child=serializers.CharField())
    follow_up_questions = serializers.ListField(child=serializers.CharField())
    possible_conditions = serializers.ListField(child=serializers.DictField())
    warning_signs = serializers.ListField(child=serializers.CharField())
    urgency_level = serializers.CharField()
    general_information = serializers.CharField()
    medication_information = serializers.ListField(child=serializers.DictField())
    recommended_next_step = serializers.CharField()
    sources = serializers.ListField(child=serializers.DictField())
    model_used = serializers.CharField()
    confidence = serializers.FloatField()
