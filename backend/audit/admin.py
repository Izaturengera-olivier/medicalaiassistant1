"""Admin registrations for audit. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog."""

    list_display = ["user", "action", "entity_type", "entity_id", "timestamp"]
    list_filter = ["action", "entity_type", "timestamp"]
    search_fields = ["user__email", "entity_type", "entity_id"]
    readonly_fields = ["user", "action", "entity_type", "entity_id", "changes", "ip_address", "user_agent", "timestamp"]
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent modification of audit logs
        return False
