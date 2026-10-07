"""HTTP endpoints for consultations. Implemented in later phases."""

from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from .models import Consultation, Symptom, PatientSymptom, FollowUpQuestion
from .serializers import (
    ConsultationSerializer,
    ConsultationCreateSerializer,
    ConsultationUpdateSerializer,
    SymptomSerializer,
    PatientSymptomSerializer,
    FollowUpQuestionSerializer
)
from accounts.permissions import IsPatient, IsDoctor, IsAdminUser


class ConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet for Consultation model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "patient", "assigned_doctor"]
    search_fields = ["chief_complaint"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "PATIENT":
            return Consultation.objects.filter(patient=user)
        elif user.role == "DOCTOR":
            return Consultation.objects.filter(assigned_doctor=user)
        elif user.role == "ADMIN":
            return Consultation.objects.all()
        return Consultation.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return ConsultationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ConsultationUpdateSerializer
        return ConsultationSerializer

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            ConsultationSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def assign_doctor(self, request, pk=None):
        """Assign a doctor to a consultation (Doctor or Admin)."""
        if request.user.role not in ["DOCTOR", "ADMIN"]:
            return Response({"error": _("Permission denied")}, status=status.HTTP_403_FORBIDDEN)

        consultation = self.get_object()
        from accounts.models import User
        
        doctor_id = request.data.get("doctor_id")
        if not doctor_id:
            return Response(
                {"error": _("doctor_id is required")},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            doctor = User.objects.get(id=doctor_id, role="DOCTOR")
            consultation.assigned_doctor = doctor
            if consultation.status == "PENDING":
                consultation.status = "IN_PROGRESS"
            consultation.save()
            return Response(
                ConsultationSerializer(consultation).data,
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": _("Doctor not found")},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Mark consultation as completed."""
        if request.user.role not in ["DOCTOR", "ADMIN"]:
            return Response({"error": _("Permission denied")}, status=status.HTTP_403_FORBIDDEN)
            
        consultation = self.get_object()
        consultation.status = "COMPLETED"
        consultation.completed_at = timezone.now()
        consultation.save()
        return Response(
            ConsultationSerializer(consultation).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def override_status(self, request, pk=None):
        """Admin/Doctor status override."""
        if request.user.role not in ["DOCTOR", "ADMIN"]:
            return Response({"error": _("Permission denied")}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        if new_status not in ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]:
            return Response({"error": _("Invalid status")}, status=status.HTTP_400_BAD_REQUEST)

        consultation = self.get_object()
        consultation.status = new_status
        if new_status == "COMPLETED":
            consultation.completed_at = timezone.now()
        consultation.save()
        return Response(ConsultationSerializer(consultation).data, status=status.HTTP_200_OK)



class SymptomViewSet(viewsets.ModelViewSet):
    """ViewSet for Symptom catalog."""

    permission_classes = [IsAuthenticated]
    queryset = Symptom.objects.all()
    serializer_class = SymptomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["name", "description"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class PatientSymptomViewSet(viewsets.ModelViewSet):
    """ViewSet for PatientSymptom."""

    permission_classes = [IsAuthenticated]
    serializer_class = PatientSymptomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["consultation", "symptom", "severity"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "PATIENT":
            return PatientSymptom.objects.filter(consultation__patient=user)
        elif user.role == "DOCTOR":
            return PatientSymptom.objects.filter(consultation__assigned_doctor=user)
        elif user.role == "ADMIN":
            return PatientSymptom.objects.all()
        return PatientSymptom.objects.none()

    def perform_create(self, serializer):
        consultation_id = self.request.data.get("consultation")
        consultation = Consultation.objects.get(id=consultation_id)
        
        # Check permissions
        if self.request.user.role == "PATIENT" and consultation.patient != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(_("You can only add symptoms to your own consultations"))
        
        serializer.save()


class FollowUpQuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for FollowUpQuestion."""

    permission_classes = [IsAuthenticated]
    serializer_class = FollowUpQuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["consultation"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "PATIENT":
            return FollowUpQuestion.objects.filter(consultation__patient=user)
        elif user.role == "DOCTOR":
            return FollowUpQuestion.objects.filter(consultation__assigned_doctor=user)
        elif user.role == "ADMIN":
            return FollowUpQuestion.objects.all()
        return FollowUpQuestion.objects.none()

    def perform_create(self, serializer):
        consultation_id = self.request.data.get("consultation")
        consultation = Consultation.objects.get(id=consultation_id)
        
        # Check permissions
        if self.request.user.role == "PATIENT" and consultation.patient != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(_("You can only add questions to your own consultations"))
        
        serializer.save()
