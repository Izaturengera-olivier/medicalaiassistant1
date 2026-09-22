from django.urls import path
from .views import analyze_symptoms, follow_up_questions, extract_symptoms, assess_urgency

urlpatterns = [
    path("analyze-symptoms/", analyze_symptoms, name="analyze_symptoms"),
    path("follow-up/", follow_up_questions, name="follow_up_questions"),
    path("extract-symptoms/", extract_symptoms, name="extract_symptoms"),
    path("assess-urgency/", assess_urgency, name="assess_urgency"),
]
