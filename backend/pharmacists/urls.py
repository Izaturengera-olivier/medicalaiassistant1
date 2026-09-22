from django.urls import path
from .views import (
    pharmacist_dashboard,
    list_prescriptions,
    get_prescription_detail,
    review_prescription,
    check_interactions
)

urlpatterns = [
    path("dashboard/", pharmacist_dashboard, name="pharmacist_dashboard"),
    path("prescriptions/", list_prescriptions, name="list_prescriptions"),
    path("prescriptions/<int:prescription_id>/", get_prescription_detail, name="get_prescription_detail"),
    path("prescriptions/<int:prescription_id>/review/", review_prescription, name="review_prescription"),
    path("medications/<int:medication_id>/interactions/", check_interactions, name="check_interactions"),
]
