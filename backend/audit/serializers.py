"""DRF serializers for audit logs."""

from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for immutable audit log entries."""

    user = UserSerializer(read_only=True)
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id", "user", "user_email", "action", "entity_type", "entity_id",
            "changes", "ip_address", "timestamp",
        ]
        read_only_fields = fields

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None
