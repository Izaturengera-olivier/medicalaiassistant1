"""HTTP endpoints for medications."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdminUserOrReadOnly
from .models import Medication, MedicationInteraction
from .serializers import MedicationSerializer, MedicationInteractionSerializer


class MedicationViewSet(viewsets.ModelViewSet):
    """Catalog of medications. Read-only for clinical/patient users, editable by Admins."""

    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        drug_class = self.request.query_params.get("drug_class")
        if search:
            queryset = queryset.filter(name__icontains=search)
        if drug_class:
            queryset = queryset.filter(drug_class=drug_class)
        return queryset

    @action(detail=True, methods=["get"])
    def interactions(self, request, pk=None):
        """Interactions involving this medication in either position."""
        medication = self.get_object()
        interactions = MedicationInteraction.objects.filter(
            medication_1=medication
        ) | MedicationInteraction.objects.filter(medication_2=medication)
        serializer = MedicationInteractionSerializer(interactions.distinct(), many=True)
        return Response({"medication": medication.name, "interactions": serializer.data})


class MedicationInteractionViewSet(viewsets.ModelViewSet):
    """Documented medication interactions. Read-only for regular users, editable by Admins."""

    queryset = MedicationInteraction.objects.all()
    serializer_class = MedicationInteractionSerializer
    permission_classes = [IsAdminUserOrReadOnly]

