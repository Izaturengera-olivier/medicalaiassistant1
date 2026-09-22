"""HTTP endpoints for patients. Implemented in later phases."""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from .models import MedicalHistory
from .serializers import MedicalHistorySerializer, MedicalHistoryCreateSerializer
from accounts.permissions import IsPatient, IsDoctor, IsAdminUser


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for MedicalHistory."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["patient", "treating_doctor"]
    search_fields = ["condition_name", "notes"]
    ordering_fields = ["diagnosis_date", "created_at"]
    ordering = ["-diagnosis_date"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "PATIENT":
            return MedicalHistory.objects.filter(patient=user)
        elif user.role == "DOCTOR":
            return MedicalHistory.objects.filter(treating_doctor=user)
        elif user.role == "ADMIN":
            return MedicalHistory.objects.all()
        return MedicalHistory.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return MedicalHistoryCreateSerializer
        return MedicalHistorySerializer


