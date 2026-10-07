from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    ForgotPasswordView,
    ResetPasswordView,
    UserProfileView,
    DoctorProfileView,
    PatientProfileView,
    PharmacistProfileView,
    UserListView,
    UserUpdateView,
    user_me
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", user_me, name="user_me"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserUpdateView.as_view(), name="user_update"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("profile/patient/", PatientProfileView.as_view(), name="patient_profile"),
    path("profile/doctor/", DoctorProfileView.as_view(), name="doctor_profile"),
    path("profile/pharmacist/", PharmacistProfileView.as_view(), name="pharmacist_profile"),
]
