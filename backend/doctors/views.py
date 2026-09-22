"""HTTP endpoints for doctors. Implemented in later phases."""

from rest_framework import status, views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count

from accounts.permissions import IsDoctor
from accounts.models import User, DoctorProfile
from consultations.models import Consultation
from .serializers import (
    DoctorProfileSerializer,
    PatientConsultationSerializer,
    ConsultationReviewSerializer,
    DoctorDashboardStatsSerializer
)
from core.constants import ConsultationStatus


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_dashboard(request):
    """
    Get doctor dashboard statistics and overview.
    """
    try:
        doctor = request.user.doctor_profile
        
        # Get all consultations assigned to this doctor
        consultations = Consultation.objects.filter(assigned_doctor=request.user)
        
        # Calculate statistics
        stats = {
            "total_patients": User.objects.filter(role="PATIENT").count(),
            "active_consultations": consultations.filter(status=ConsultationStatus.IN_PROGRESS).count(),
            "completed_consultations": consultations.filter(status=ConsultationStatus.COMPLETED).count(),
            "pending_reviews": consultations.filter(status=ConsultationStatus.IN_PROGRESS).count(),
            "urgent_cases": consultations.filter(
                ai_assessment__urgency_level="URGENT_MEDICAL_ATTENTION"
            ).distinct().count()
        }
        
        # Get recent consultations
        recent_consultations = consultations.order_by("-created_at")[:5]
        recent_data = PatientConsultationSerializer(recent_consultations, many=True).data
        
        return Response({
            "stats": stats,
            "recent_consultations": recent_data
        }, status=status.HTTP_200_OK)
        
    except DoctorProfile.DoesNotExist:
        return Response(
            {"error": _("Doctor profile not found")},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def list_assigned_patients(request):
    """
    List all patients assigned to or seen by this doctor.
    """
    try:
        # Get all consultations where this doctor is assigned
        consultations = Consultation.objects.filter(assigned_doctor=request.user)
        
        # Get unique patients
        patient_ids = consultations.values_list("patient_id", flat=True).distinct()
        patients = User.objects.filter(id__in=patient_ids)
        
        patient_data = []
        for patient in patients:
            # Get latest consultation
            latest_consultation = consultations.filter(patient=patient).order_by("-created_at").first()
            
            patient_data.append({
                "id": patient.id,
                "name": patient.get_full_name(),
                "email": patient.email,
                "last_consultation": latest_consultation.created_at if latest_consultation else None,
                "consultation_count": consultations.filter(patient=patient).count()
            })
        
        return Response({
            "patients": patient_data,
            "total": len(patient_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def list_consultations(request):
    """
    List all consultations for this doctor with optional filtering.
    """
    try:
        status_filter = request.query_params.get("status")
        consultations = Consultation.objects.filter(assigned_doctor=request.user)
        
        if status_filter:
            consultations = consultations.filter(status=status_filter)
        
        consultations = consultations.order_by("-created_at")
        
        data = PatientConsultationSerializer(consultations, many=True).data
        
        return Response({
            "consultations": data,
            "total": len(data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def get_consultation_detail(request, consultation_id: int):
    """
    Get detailed information about a specific consultation.
    """
    try:
        consultation = Consultation.objects.get(
            id=consultation_id,
            assigned_doctor=request.user
        )
        
        data = PatientConsultationSerializer(consultation).data
        
        # Add patient medical history
        from patients.models import MedicalHistory
        medical_history = MedicalHistory.objects.filter(patient=consultation.patient)
        data["medical_history"] = [
            {
                "condition_name": h.condition_name,
                "diagnosis_date": h.diagnosis_date,
                "notes": h.notes
            }
            for h in medical_history
        ]
        
        return Response(data, status=status.HTTP_200_OK)
        
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
@permission_classes([IsAuthenticated, IsDoctor])
def review_consultation(request, consultation_id: int):
    """
    Review and update a consultation with doctor's assessment.
    """
    serializer = ConsultationReviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        consultation = Consultation.objects.get(
            id=consultation_id,
            assigned_doctor=request.user
        )
        
        # Update consultation
        consultation.status = serializer.validated_data["status"]
        consultation.doctor_notes = serializer.validated_data.get("notes", "")
        consultation.diagnosis = serializer.validated_data.get("diagnosis", "")
        consultation.treatment_recommendation = serializer.validated_data.get("treatment_recommendation", "")
        consultation.follow_up_required = serializer.validated_data.get("follow_up_required", False)
        consultation.ai_assessment_accepted = serializer.validated_data.get("accept_ai_assessment", False)
        consultation.save()
        
        return Response({
            "message": _("Consultation reviewed successfully"),
            "consultation_id": consultation.id,
            "status": consultation.status
        }, status=status.HTTP_200_OK)
        
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
@permission_classes([IsAuthenticated, IsDoctor])
def assign_consultation(request, consultation_id: int):
    """
    Assign a consultation to this doctor.
    """
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        
        if consultation.assigned_doctor and consultation.assigned_doctor != request.user:
            return Response(
                {"error": _("Consultation is already assigned to another doctor")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consultation.assigned_doctor = request.user
        consultation.status = ConsultationStatus.IN_PROGRESS
        consultation.save()
        
        return Response({
            "message": _("Consultation assigned successfully"),
            "consultation_id": consultation.id
        }, status=status.HTTP_200_OK)
        
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
