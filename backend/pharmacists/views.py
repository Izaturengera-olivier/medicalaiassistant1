"""HTTP endpoints for pharmacists. Implemented in later phases."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from datetime import datetime, timedelta

from accounts.permissions import IsPharmacist
from accounts.models import User, PharmacistProfile
from medications.models import Prescription, MedicationInteraction
from .serializers import (
    PharmacistProfileSerializer,
    PrescriptionSerializer,
    MedicationSafetyReviewSerializer,
    PharmacistDashboardStatsSerializer
)
from core.constants import PrescriptionStatus


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPharmacist])
def pharmacist_dashboard(request):
    """
    Get pharmacist dashboard statistics and overview.
    """
    try:
        # Get all prescriptions
        all_prescriptions = Prescription.objects.all()
        
        # Calculate statistics
        today = datetime.now().date()
        stats = {
            "total_prescriptions": all_prescriptions.count(),
            "pending_reviews": all_prescriptions.filter(status=PrescriptionStatus.ACTIVE).count(),
            "approved_today": all_prescriptions.filter(
                status=PrescriptionStatus.ACTIVE,
                prescribed_at__date=today
            ).count(),
            "flagged_prescriptions": all_prescriptions.filter(
                pharmacist_notes__icontains="flag"
            ).count()
        }
        
        # Get recent prescriptions
        recent_prescriptions = all_prescriptions.order_by("-prescribed_at")[:5]
        recent_data = PrescriptionSerializer(recent_prescriptions, many=True).data
        
        return Response({
            "stats": stats,
            "recent_prescriptions": recent_data
        }, status=status.HTTP_200_OK)
        
    except PharmacistProfile.DoesNotExist:
        return Response(
            {"error": _("Pharmacist profile not found")},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPharmacist])
def list_prescriptions(request):
    """
    List all prescriptions with optional filtering.
    """
    try:
        status_filter = request.query_params.get("status")
        prescriptions = Prescription.objects.all()
        
        if status_filter:
            prescriptions = prescriptions.filter(status=status_filter)
        
        prescriptions = prescriptions.order_by("-prescribed_at")
        
        data = PrescriptionSerializer(prescriptions, many=True).data
        
        return Response({
            "prescriptions": data,
            "total": len(data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPharmacist])
def get_prescription_detail(request, prescription_id: int):
    """
    Get detailed information about a specific prescription.
    """
    try:
        prescription = Prescription.objects.get(id=prescription_id)
        
        data = PrescriptionSerializer(prescription).data
        
        # Add patient allergy information
        from accounts.models import PatientProfile
        try:
            patient_profile = prescription.patient.patient_profile
            data["patient_allergies"] = patient_profile.allergies
            data["patient_chronic_conditions"] = patient_profile.chronic_conditions
        except PatientProfile.DoesNotExist:
            data["patient_allergies"] = []
            data["patient_chronic_conditions"] = []
        
        # Check for medication interactions
        interactions = MedicationInteraction.objects.filter(
            medication_1=prescription.medication
        )
        data["interaction_count"] = interactions.count()
        
        return Response(data, status=status.HTTP_200_OK)
        
    except Prescription.DoesNotExist:
        return Response(
            {"error": _("Prescription not found")},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsPharmacist])
def review_prescription(request, prescription_id: int):
    """
    Review a prescription for medication safety.
    """
    serializer = MedicationSafetyReviewSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        prescription = Prescription.objects.get(id=prescription_id)
        
        # Update prescription based on review
        if serializer.validated_data["review_status"] == "APPROVED":
            prescription.status = PrescriptionStatus.ACTIVE
        elif serializer.validated_data["review_status"] == "REJECTED":
            prescription.status = PrescriptionStatus.DISCONTINUED
        elif serializer.validated_data["review_status"] == "FLAGGED":
            prescription.status = PrescriptionStatus.ACTIVE  # Still active but flagged
        
        prescription.pharmacist_notes = serializer.validated_data.get("pharmacist_notes", "")
        prescription.interaction_flags = serializer.validated_data.get("interaction_flags", [])
        prescription.save()
        
        return Response({
            "message": _("Prescription reviewed successfully"),
            "prescription_id": prescription.id,
            "status": prescription.status
        }, status=status.HTTP_200_OK)
        
    except Prescription.DoesNotExist:
        return Response(
            {"error": _("Prescription not found")},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPharmacist])
def check_interactions(request, medication_id: int):
    """
    Check for medication interactions for a specific medication.
    """
    try:
        from medications.models import Medication
        medication = Medication.objects.get(id=medication_id)
        
        interactions = MedicationInteraction.objects.filter(medication=medication)
        
        interaction_data = [
            {
                "id": interaction.id,
                "interacting_medication": interaction.interacting_medication.name,
                "severity": interaction.severity,
                "description": interaction.description,
                "recommendation": interaction.recommendation
            }
            for interaction in interactions
        ]
        
        return Response({
            "medication": medication.name,
            "interactions": interaction_data,
            "total": len(interaction_data)
        }, status=status.HTTP_200_OK)
        
    except Medication.DoesNotExist:
        return Response(
            {"error": _("Medication not found")},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
