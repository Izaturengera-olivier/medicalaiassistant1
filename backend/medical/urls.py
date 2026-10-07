from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MedicalConditionViewSet

router = DefaultRouter()
router.register(r"conditions", MedicalConditionViewSet, basename="medical-condition")

urlpatterns = [
    path("", include(router.urls)),
]
