from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ConsultationViewSet, SymptomViewSet, PatientSymptomViewSet, FollowUpQuestionViewSet

router = DefaultRouter()
router.register(r"consultations", ConsultationViewSet, basename="consultation")
router.register(r"symptoms", SymptomViewSet, basename="symptom")
router.register(r"patient-symptoms", PatientSymptomViewSet, basename="patient-symptom")
router.register(r"follow-up-questions", FollowUpQuestionViewSet, basename="follow-up-question")

urlpatterns = [
    path("", include(router.urls)),
]
