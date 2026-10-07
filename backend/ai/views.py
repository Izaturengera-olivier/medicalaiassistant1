"""HTTP endpoints for ai. Implemented in later phases."""

from rest_framework import status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import AIAssessment, ChatConversation, ChatMessage, PossibleCondition
from .serializers import (
    AIAssessmentSerializer,
    AIAnalysisRequestSerializer,
    AIAnalysisResponseSerializer,
    AIProfessionalChatRequestSerializer,
    ChatConversationDetailSerializer,
    ChatConversationListSerializer,
)
from .services import AIService, SymptomAnalysisService, TriageService
from consultations.models import Consultation, FollowUpQuestion
from core.constants import SourceType, UserRole
from knowledge.models import MedicalKnowledgeSource, RetrievedEvidence

_PROFESSIONAL_ROLES = {UserRole.DOCTOR, UserRole.PHARMACIST, UserRole.ADMIN}


def _resolve_conversation(user, conversation_id, kind, first_message):
    """Return the saved conversation to continue, creating one on first message."""
    if conversation_id:
        conversation = ChatConversation.objects.filter(
            id=conversation_id, user=user, kind=kind
        ).first()
        if conversation:
            return conversation
    return ChatConversation.objects.create(
        user=user, kind=kind, title=first_message[:120]
    )


def _persist_exchange(conversation, user_message, reply, details):
    """Save both turns of an exchange and bump the conversation's activity."""
    ChatMessage.objects.create(
        conversation=conversation, role="user", content=user_message
    )
    ChatMessage.objects.create(
        conversation=conversation, role="assistant", content=reply, details=details
    )
    conversation.save(update_fields=["updated_at"])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyze_symptoms(request):
    """
    Continue the AI conversation with a patient.

    Searches all approved medical sources for evidence, generates a
    conversational reply with follow-up questions, and persists the
    assessment, follow-up questions, and retrieved evidence when a
    consultation is attached.
    """
    serializer = AIAnalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        patient_input = data["patient_input"]
        consultation = None
        if data.get("consultation_id"):
            try:
                consultation = Consultation.objects.get(
                    id=data["consultation_id"], patient=request.user
                )
            except Consultation.DoesNotExist:
                return Response(
                    {"error": _("Consultation not found")},
                    status=status.HTTP_404_NOT_FOUND
                )

        ai_service = AIService()
        assessment = ai_service.converse(
            message=patient_input,
            history=data.get("history", []),
            patient_history=data.get("patient_history"),
            current_medications=data.get("current_medications", [])
        )
        evidence = assessment.pop("evidence", [])

        if consultation:
            ai_assessment = _persist_assessment(
                consultation, assessment, evidence, patient_input
            )
            assessment["id"] = ai_assessment.id
            assessment["consultation_id"] = consultation.id

        conversation = _resolve_conversation(
            request.user, data.get("conversation_id"), "patient", patient_input
        )
        _persist_exchange(
            conversation,
            patient_input,
            assessment.get("reply") or assessment.get("general_information") or "",
            assessment,
        )
        assessment["conversation_id"] = conversation.id

        response_serializer = AIAnalysisResponseSerializer(assessment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def professional_chat(request):
    """
    Continue the AI decision-support conversation with a clinician.

    Available to doctors, pharmacists, and admins. Searches all approved
    medical sources for evidence and answers at clinician level (differentials,
    medication information, interactions, guideline-based next steps) without
    attaching or persisting a patient consultation.
    """
    if request.user.role not in _PROFESSIONAL_ROLES:
        return Response(
            {"error": _("This endpoint is only available to clinical staff.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AIProfessionalChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = serializer.validated_data
        ai_service = AIService()
        result = ai_service.converse_professional(
            message=data["message"],
            history=data.get("history", []),
            professional_context=data.get("context"),
        )
        result.pop("evidence", None)

        conversation = _resolve_conversation(
            request.user, data.get("conversation_id"), "professional", data["message"]
        )
        _persist_exchange(
            conversation,
            data["message"],
            result.get("reply") or result.get("general_information") or "",
            result,
        )
        result["conversation_id"] = conversation.id

        response_serializer = AIAnalysisResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _persist_assessment(consultation, assessment, evidence, patient_input):
    """Store the latest assessment, follow-up questions, and evidence."""
    ai_assessment, _created = AIAssessment.objects.update_or_create(
        consultation=consultation,
        defaults={
            "symptoms_identified": assessment["symptoms_identified"],
            "follow_up_questions": assessment["follow_up_questions"],
            "possible_conditions_list": assessment["possible_conditions"],
            "warning_signs": assessment["warning_signs"],
            "urgency_level": assessment["urgency_level"],
            "general_information": assessment["general_information"],
            "medication_information": assessment["medication_information"],
            "recommended_next_step": assessment["recommended_next_step"],
            "sources": assessment["sources"],
            "model_used": assessment["model_used"],
        },
    )

    ai_assessment.identified_conditions.all().delete()
    for condition_data in assessment["possible_conditions"]:
        PossibleCondition.objects.create(
            ai_assessment=ai_assessment,
            condition_name=condition_data["name"],
            likelihood=condition_data["likelihood"],
            confidence_level=condition_data.get("confidence", "medium"),
            reasoning=condition_data.get("description", "")
        )

    # The patient's latest message answers whichever questions were still open.
    FollowUpQuestion.objects.filter(
        consultation=consultation, answered_at__isnull=True
    ).update(answer=patient_input, answered_at=timezone.now())
    for question in assessment["follow_up_questions"]:
        if not FollowUpQuestion.objects.filter(
            consultation=consultation, question=question
        ).exists():
            FollowUpQuestion.objects.create(consultation=consultation, question=question)

    RetrievedEvidence.objects.filter(ai_assessment=ai_assessment).delete()
    for item in evidence:
        RetrievedEvidence.objects.create(
            ai_assessment=ai_assessment,
            source=_resolve_source(item),
            title=item.get("title") or "",
            url=item.get("url") or "",
            extracted_content=item.get("content") or "",
            relevance_score=item.get("relevance_score") or 0.0,
        )

    return ai_assessment


def _resolve_source(evidence_item):
    """Get or create the DB record for the source an evidence item came from."""
    source_type = evidence_item.get("source_type") or ""
    if source_type not in dict(SourceType.CHOICES):
        source_type = SourceType.LITERATURE
    source, _created = MedicalKnowledgeSource.objects.get_or_create(
        name=evidence_item.get("source_name") or "Unknown",
        defaults={
            "url": evidence_item.get("url") or "",
            "source_type": source_type,
            "approval_status": "approved",
        },
    )
    return source


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    """List the current user's saved chat conversations, newest first."""
    queryset = ChatConversation.objects.filter(user=request.user)
    kind = request.query_params.get("kind")
    if kind in ("patient", "professional"):
        queryset = queryset.filter(kind=kind)
    page = queryset.order_by("-updated_at")[:200]
    return Response(ChatConversationListSerializer(page, many=True).data)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    """Retrieve (with messages) or delete one of the user's conversations."""
    conversation = ChatConversation.objects.filter(id=pk, user=request.user).first()
    if conversation is None:
        return Response(
            {"error": _("Conversation not found")},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "DELETE":
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(ChatConversationDetailSerializer(conversation).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def follow_up_questions(request):
    """
    Generate follow-up questions based on current consultation context.
    """
    consultation_id = request.data.get("consultation_id")
    current_symptoms = request.data.get("current_symptoms", [])
    
    if not consultation_id:
        return Response(
            {"error": _("consultation_id is required")},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        consultation = Consultation.objects.get(id=consultation_id, patient=request.user)
        
        consultation_context = {
            "chief_complaint": consultation.chief_complaint,
            "status": consultation.status,
            "created_at": consultation.created_at.isoformat()
        }
        
        ai_service = AIService()
        questions = ai_service.generate_follow_up_questions(
            consultation_context=consultation_context,
            current_symptoms=current_symptoms
        )
        
        return Response({"questions": questions}, status=status.HTTP_200_OK)
        
    except Consultation.DoesNotExist:
        return Response(
            {"error": _("Consultation not found")},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def extract_symptoms(request):
    """
    Extract symptoms from natural language input using pattern matching.
    """
    text = request.data.get("text", "")
    
    if not text:
        return Response(
            {"error": _("text is required")},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        symptom_service = SymptomAnalysisService()
        analysis = symptom_service.analyze_symptom_description(text)
        
        return Response(analysis, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assess_urgency(request):
    """
    Assess medical urgency based on symptoms and patient input.
    """
    symptoms = request.data.get("symptoms", [])
    patient_input = request.data.get("patient_input", "")
    
    if not patient_input:
        return Response(
            {"error": _("patient_input is required")},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        triage_service = TriageService()
        urgency_level = triage_service.assess_urgency(symptoms, patient_input)
        recommendation = triage_service.get_triage_recommendation(urgency_level)
        warning_signs = triage_service.identify_warning_signs(patient_input, symptoms)
        
        return Response({
            "urgency_level": urgency_level,
            "recommendation": recommendation,
            "warning_signs": warning_signs,
            "disclaimer": triage_service.generate_disclaimer()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
