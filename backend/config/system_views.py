"""API endpoints for Admin System Settings and Control Panel."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.permissions import IsAdminUser

# In-memory / persistent runtime settings storage
_SYSTEM_SETTINGS = {
    "ai_provider": "mock",
    "ai_triage_mode": "STRICT",
    "web_search_enabled": True,
    "maintenance_mode": False,
    "system_notice": "System operating normally. All clinical safety filters enabled.",
    "allow_registration": True,
    "last_updated": timezone.now().isoformat(),
}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_system_settings(request):
    """Retrieve system configuration settings."""
    return Response(_SYSTEM_SETTINGS, status=status.HTTP_200_OK)


@api_view(["POST", "PUT"])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_system_settings(request):
    """Update runtime system configuration settings (Admin only)."""
    data = request.data
    valid_keys = {"ai_provider", "ai_triage_mode", "web_search_enabled", "maintenance_mode", "system_notice", "allow_registration"}
    
    for key in valid_keys:
        if key in data:
            _SYSTEM_SETTINGS[key] = data[key]
            
    _SYSTEM_SETTINGS["last_updated"] = timezone.now().isoformat()
    return Response({
        "message": _("System settings updated successfully."),
        "settings": _SYSTEM_SETTINGS
    }, status=status.HTTP_200_OK)
