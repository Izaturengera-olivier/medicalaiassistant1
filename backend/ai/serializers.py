"""DRF serializers for ai. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import AIAssessment, ChatConversation, ChatMessage, PossibleCondition


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


class ConversationMessageSerializer(serializers.Serializer):
    """A single turn in the patient conversation."""

    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField(max_length=4000)


class AIAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for AI analysis request."""

    patient_input = serializers.CharField(
        help_text=_("Patient's description of symptoms")
    )
    consultation_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text=_("Existing consultation to attach the assessment to")
    )
    conversation_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text=_("Saved chat conversation to continue")
    )
    history = ConversationMessageSerializer(
        many=True,
        required=False,
        help_text=_("Previous conversation turns, oldest first")
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


class AIProfessionalChatRequestSerializer(serializers.Serializer):
    """Request for the clinician-facing decision support conversation."""

    message = serializers.CharField(
        help_text=_("The clinician's question or latest message")
    )
    conversation_id = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text=_("Saved chat conversation to continue")
    )
    history = ConversationMessageSerializer(
        many=True,
        required=False,
        help_text=_("Previous conversation turns, oldest first")
    )
    context = serializers.JSONField(
        required=False,
        help_text=_(
            "Optional case details supplied by the clinician "
            "(patient summary, medications, role, ...)"
        )
    )


class AIAnalysisResponseSerializer(serializers.Serializer):
    """Serializer for AI analysis response."""

    id = serializers.IntegerField(required=False)
    consultation_id = serializers.IntegerField(required=False)
    conversation_id = serializers.IntegerField(required=False)
    reply = serializers.CharField()
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


class ChatMessageSerializer(serializers.ModelSerializer):
    """A saved message inside a chat conversation."""

    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "details", "created_at"]


class ChatConversationListSerializer(serializers.ModelSerializer):
    """Conversation summary for the sidebar list."""

    class Meta:
        model = ChatConversation
        fields = ["id", "title", "kind", "created_at", "updated_at"]


class ChatConversationDetailSerializer(ChatConversationListSerializer):
    """A conversation with all of its messages."""

    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta(ChatConversationListSerializer.Meta):
        fields = ChatConversationListSerializer.Meta.fields + ["messages"]
