from django.urls import path
from .views import (
    analyze_symptoms,
    conversation_detail,
    conversation_list,
    follow_up_questions,
    extract_symptoms,
    assess_urgency,
    medical_document_detail,
    medical_document_list,
    professional_chat,
    upload_and_analyze_document,
)

urlpatterns = [
    path("analyze-symptoms/", analyze_symptoms, name="analyze_symptoms"),
    path("professional-chat/", professional_chat, name="professional_chat"),
    path("upload-and-analyze/", upload_and_analyze_document, name="upload_and_analyze_document"),
    path("documents/", medical_document_list, name="medical_document_list"),
    path("documents/<int:pk>/", medical_document_detail, name="medical_document_detail"),
    path("conversations/", conversation_list, name="conversation_list"),
    path("conversations/<int:pk>/", conversation_detail, name="conversation_detail"),
    path("follow-up/", follow_up_questions, name="follow_up_questions"),
    path("extract-symptoms/", extract_symptoms, name="extract_symptoms"),
    path("assess-urgency/", assess_urgency, name="assess_urgency"),
]
