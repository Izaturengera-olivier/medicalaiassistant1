from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Unauthenticated liveness check. Does not query patient data."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "clinical-cds",
                "phase": 1,
                "disclaimer": (
                    "Decision-support system only. Not a substitute for professional "
                    "diagnosis, prescription, or treatment."
                ),
            }
        )
