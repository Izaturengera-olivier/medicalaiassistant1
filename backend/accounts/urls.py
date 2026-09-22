from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserProfileView,
    PatientProfileView,
    DoctorProfileView,
    PharmacistProfileView,
    user_me
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", user_me, name="user_me"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("profile/patient/", PatientProfileView.as_view(), name="patient_profile"),
    path("profile/doctor/", DoctorProfileView.as_view(), name="doctor_profile"),
    path("profile/pharmacist/", PharmacistProfileView.as_view(), name="pharmacist_profile"),
]
