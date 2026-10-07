"""HTTP endpoints for audit logs. Admin-only."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminUser

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only, admin-only audit log."""

    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        action_filter = self.request.query_params.get("action")
        entity_type = self.request.query_params.get("entity_type")
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)
        return queryset
