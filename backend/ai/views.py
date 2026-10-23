"""HTTP endpoints for ai. Implemented in later phases."""

import logging

from rest_framework import status, views
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import AIAssessment, ChatConversation, ChatMessage, MedicalDocument, PossibleCondition
from .serializers import (
    AIAssessmentSerializer,
    AIAnalysisRequestSerializer,
    AIAnalysisResponseSerializer,
    AIProfessionalChatRequestSerializer,
    ChatConversationDetailSerializer,
    ChatConversationListSerializer,
    DocumentAnalysisResponseSerializer,
    DocumentUploadAnalysisRequestSerializer,
    MedicalDocumentSerializer,
)
from .services import AIService, DocumentParserService, SymptomAnalysisService, TriageService
from consultations.models import Consultation, FollowUpQuestion
from core.constants import SourceType, UserRole
from core.exceptions import DocumentParseError
from knowledge.models import MedicalKnowledgeSource, RetrievedEvidence

logger = logging.getLogger(__name__)

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
        
        assessment = getattr(consultation, "ai_assessment", None)
        consultation_context = {
            "chief_complaint": consultation.chief_complaint,
            "notes": consultation.doctor_notes,
            "status": consultation.status,
            "created_at": consultation.created_at.isoformat(),
            "symptoms": list(assessment.symptoms_identified or []) if assessment else [],
            "already_asked": list(assessment.follow_up_questions or []) if assessment else [],
        }
        recorded_symptoms = [
            ps.symptom.name for ps in consultation.patient_symptoms.select_related("symptom")
        ]
        if not current_symptoms:
            current_symptoms = recorded_symptoms
        
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upload_and_analyze_document(request):
    """
    Upload a medical document (scanner result, CT/MRI, X-ray, lab report, pathology)
    and perform deep AI clinical analysis grounded in trusted medical solutions.
    """
    serializer = DocumentUploadAnalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        uploaded_file = serializer.validated_data["file"]
        user_message = serializer.validated_data.get("message", "")
        consultation_id = serializer.validated_data.get("consultation_id")
        conversation_id = serializer.validated_data.get("conversation_id")
        kind = serializer.validated_data.get("kind", "patient")

        # Parse document and extract text & clinical metadata
        parser_svc = DocumentParserService()
        parsed = parser_svc.parse_file(
            file_obj=uploaded_file,
            filename=uploaded_file.name,
            content_type=getattr(uploaded_file, "content_type", "")
        )

        consultation = None
        if consultation_id:
            try:
                if request.user.role == UserRole.PATIENT:
                    consultation = Consultation.objects.get(id=consultation_id, patient=request.user)
                else:
                    consultation = Consultation.objects.get(id=consultation_id)
            except Consultation.DoesNotExist:
                return Response({"error": _("Consultation not found")}, status=status.HTTP_404_NOT_FOUND)

        # Resolve or create conversation
        initial_title = user_message.strip() or f"Scan: {uploaded_file.name}"
        conversation = _resolve_conversation(request.user, conversation_id, kind, initial_title[:120])

        # Persist the uploaded medical document record
        doc_record = MedicalDocument.objects.create(
            user=request.user,
            consultation=consultation,
            conversation=conversation,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_type=getattr(uploaded_file, "content_type", "") or "",
            file_size=parsed["file_size"],
            document_category=parsed["category"],
            extracted_text=parsed["text"][:30000],
        )

        # Perform intelligent clinical analysis grounded in trusted sources
        ai_service = AIService()
        analysis = ai_service.analyze_medical_document(
            document_text=parsed["text"] or f"File uploaded: {uploaded_file.name}",
            document_category=parsed["category"],
            exam_type=parsed["exam_type"],
            user_message=user_message,
            user_role=request.user.role,
        )

        # Update document with analysis
        doc_record.ai_analysis = analysis
        doc_record.save(update_fields=["ai_analysis"])

        # Persist user chat message with attached document
        user_display_text = user_message.strip() or f"Uploaded report: {uploaded_file.name}"
        ChatMessage.objects.create(
            conversation=conversation,
            role="user",
            content=user_display_text,
            document=doc_record,
            details={
                "attachment": {
                    "document_id": doc_record.id,
                    "file_name": doc_record.file_name,
                    "file_url": doc_record.file.url if doc_record.file else "",
                    "file_size": doc_record.file_size,
                    "category": doc_record.document_category,
                    "exam_type": parsed["exam_type"],
                }
            }
        )

        # Persist assistant reply with structured analysis
        ChatMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=analysis.get("reply", ""),
            details=analysis
        )
        conversation.save(update_fields=["updated_at"])

        # Construct response
        response_payload = {
            "document_id": doc_record.id,
            "file_name": doc_record.file_name,
            "file_url": doc_record.file.url if doc_record.file else "",
            "document_category": doc_record.document_category,
            "exam_type": analysis.get("exam_type", parsed["exam_type"]),
            "document_summary": analysis.get("document_summary", ""),
            "scan_findings": analysis.get("scan_findings", []),
            "abnormalities": analysis.get("abnormalities", []),
            "possible_conditions": analysis.get("possible_conditions", []),
            "warning_signs": analysis.get("warning_signs", []),
            "urgency_level": analysis.get("urgency_level", "INFORMATIONAL"),
            "trusted_solutions": analysis.get("trusted_solutions", []),
            "recommended_next_step": analysis.get("recommended_next_step", ""),
            "reply": analysis.get("reply", ""),
            "sources": analysis.get("sources", []),
            "conversation_id": conversation.id,
            "consultation_id": consultation.id if consultation else None,
            "confidence": analysis.get("confidence", 0.9),
        }

        resp_serializer = DocumentAnalysisResponseSerializer(response_payload)
        return Response(resp_serializer.data, status=status.HTTP_201_CREATED)

    except DocumentParseError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as exc:
        logger.exception("Document upload and analysis failed")
        return Response(
            {"error": _("Document analysis failed. Please try again.")},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def medical_document_list(request):
    """List uploaded medical documents for the current user."""
    docs = MedicalDocument.objects.filter(user=request.user).order_by("-created_at")[:100]
    return Response(MedicalDocumentSerializer(docs, many=True).data)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def medical_document_detail(request, pk):
    """Retrieve or delete an uploaded medical document."""
    doc = MedicalDocument.objects.filter(id=pk, user=request.user).first()
    if not doc:
        return Response({"error": _("Document not found")}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        doc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(MedicalDocumentSerializer(doc).data)
