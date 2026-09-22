from django.urls import path
from .views import (
    doctor_dashboard,
    list_assigned_patients,
    list_consultations,
    get_consultation_detail,
    review_consultation,
    assign_consultation
)

urlpatterns = [
    path("dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("patients/", list_assigned_patients, name="list_assigned_patients"),
    path("consultations/", list_consultations, name="list_consultations"),
    path("consultations/<int:consultation_id>/", get_consultation_detail, name="get_consultation_detail"),
    path("consultations/<int:consultation_id>/review/", review_consultation, name="review_consultation"),
    path("consultations/<int:consultation_id>/assign/", assign_consultation, name="assign_consultation"),
]
