"""HTTP endpoints for accounts. Implemented in later phases."""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.translation import gettext_lazy as _

from .models import User, PatientProfile, DoctorProfile, PharmacistProfile
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PatientProfileSerializer,
    DoctorProfileSerializer,
    PharmacistProfileSerializer
)
from .permissions import IsPatient, IsDoctor, IsPharmacist, IsAdminUser


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create appropriate profile based on role
        if user.role == "PATIENT":
            PatientProfile.objects.create(user=user)
        elif user.role == "DOCTOR":
            DoctorProfile.objects.create(user=user)
        elif user.role == "PHARMACIST":
            PharmacistProfile.objects.create(user=user)
        
        return Response(
            {
                "message": _("User registered successfully"),
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view with additional user data."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Add user data to response
            user = User.objects.get(email=request.data.get("email"))
            response.data["user"] = UserSerializer(user).data
        
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update current user profile."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class PatientProfileView(generics.RetrieveUpdateAPIView):
    """Get and update patient profile."""

    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, IsPatient]

    def get_object(self):
        profile, created = PatientProfile.objects.get_or_create(user=self.request.user)
        return profile


class DoctorProfileView(generics.RetrieveUpdateAPIView):
    """Get and update doctor profile."""

    serializer_class = DoctorProfileSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_object(self):
        profile, created = DoctorProfile.objects.get_or_create(user=self.request.user)
        return profile


class PharmacistProfileView(generics.RetrieveUpdateAPIView):
    """Get and update pharmacist profile."""

    serializer_class = PharmacistProfileSerializer
    permission_classes = [IsAuthenticated, IsPharmacist]

    def get_object(self):
        profile, created = PharmacistProfile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_me(request):
    """Get current user information."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
