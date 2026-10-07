from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MedicationViewSet, MedicationInteractionViewSet

router = DefaultRouter()
router.register(r"medications", MedicationViewSet, basename="medication")
router.register(r"interactions", MedicationInteractionViewSet, basename="medication-interaction")

urlpatterns = [
    path("", include(router.urls)),
]
