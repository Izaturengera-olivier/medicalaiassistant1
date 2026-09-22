"""Domain models for audit. Implemented in Phase 2.

Immutable audit log for access and AI events.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class AuditLog(models.Model):
    """Immutable audit log for system events."""

    ACTION_TYPES = [
        ("create", _("Create")),
        ("read", _("Read")),
        ("update", _("Update")),
        ("delete", _("Delete")),
        ("login", _("Login")),
        ("logout", _("Logout")),
        ("ai_assessment", _("AI Assessment")),
        ("medical_record_access", _("Medical Record Access")),
        ("prescription_access", _("Prescription Access")),
        ("other", _("Other")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("user")
    )
    action = models.CharField(
        max_length=30,
        choices=ACTION_TYPES,
        verbose_name=_("action")
    )
    entity_type = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Type of entity affected (e.g., Consultation, Prescription)")
    )
    entity_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("ID of the entity affected")
    )
    changes = models.JSONField(
        _("changes"),
        default=dict,
        blank=True,
        help_text=_("Details of changes made")
    )
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
        help_text=_("IP address of the request")
    )
    user_agent = models.TextField(
        _("user agent"),
        blank=True,
        help_text=_("Browser/user agent string")
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        verbose_name = _("audit log")
        verbose_name_plural = _("audit logs")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["action", "timestamp"]),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        return f"{user_str} - {self.action} on {self.entity_type or 'N/A'} at {self.timestamp}"
