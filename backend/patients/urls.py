from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MedicalHistoryViewSet

router = DefaultRouter()
router.register(r"medical-history", MedicalHistoryViewSet, basename="medical-history")

urlpatterns = [
    path("", include(router.urls)),
]
