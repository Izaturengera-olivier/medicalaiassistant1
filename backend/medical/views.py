"""HTTP endpoints for medical conditions."""

from rest_framework import viewsets
from accounts.permissions import IsAdminUserOrReadOnly

from .models import MedicalCondition
from .serializers import MedicalConditionSerializer


class MedicalConditionViewSet(viewsets.ModelViewSet):
    """Catalog of medical conditions. Read-only for clinical/patient users, editable by Admins."""

    queryset = MedicalCondition.objects.all()
    serializer_class = MedicalConditionSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        category = self.request.query_params.get("category")
        if search:
            queryset = queryset.filter(name__icontains=search)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

