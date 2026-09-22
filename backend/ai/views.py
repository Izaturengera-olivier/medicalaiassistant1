"""HTTP endpoints for ai. Implemented in later phases."""

from rest_framework import status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from .serializers import (
    AIAssessmentSerializer,
    AIAnalysisRequestSerializer,
    AIAnalysisResponseSerializer
)
from .services import AIService, SymptomAnalysisService, TriageService
from consultations.models import Consultation


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyze_symptoms(request):
    """
    Analyze patient symptoms and generate AI assessment.
    """
    serializer = AIAnalysisRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        patient_input = serializer.validated_data["patient_input"]
        patient_history = serializer.validated_data.get("patient_history")
        current_medications = serializer.validated_data.get("current_medications", [])
        
        # Use AI service for analysis
        ai_service = AIService()
        assessment = ai_service.analyze_symptoms(
            patient_input=patient_input,
            patient_history=patient_history,
            current_medications=current_medications
        )
        
        # If consultation_id is provided, save the assessment
        consultation_id = request.data.get("consultation_id")
        if consultation_id:
            try:
                consultation = Consultation.objects.get(id=consultation_id, patient=request.user)
                # Save assessment to database
                from .models import AIAssessment, PossibleCondition
                
                ai_assessment = AIAssessment.objects.create(
                    consultation=consultation,
                    symptoms_identified=assessment["symptoms_identified"],
                    follow_up_questions=assessment["follow_up_questions"],
                    possible_conditions_list=assessment["possible_conditions"],
                    warning_signs=assessment["warning_signs"],
                    urgency_level=assessment["urgency_level"],
                    general_information=assessment["general_information"],
                    medication_information=assessment["medication_information"],
                    recommended_next_step=assessment["recommended_next_step"],
                    sources=assessment["sources"],
                    model_used=assessment["model_used"]
                )
                
                # Save possible conditions
                for condition_data in assessment["possible_conditions"]:
                    PossibleCondition.objects.create(
                        ai_assessment=ai_assessment,
                        condition_name=condition_data["name"],
                        likelihood=condition_data["likelihood"],
                        confidence_level=condition_data.get("confidence", "medium"),
                        reasoning=condition_data.get("description", "")
                    )
                
                assessment["id"] = ai_assessment.id
                assessment["consultation_id"] = consultation_id
                
            except Consultation.DoesNotExist:
                return Response(
                    {"error": _("Consultation not found")},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        response_serializer = AIAnalysisResponseSerializer(assessment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
