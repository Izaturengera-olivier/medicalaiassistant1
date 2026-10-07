"""HTTP endpoints for accounts. Implemented in later phases."""

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.translation import gettext_lazy as _

from .models import User, PatientProfile, DoctorProfile, PharmacistProfile, PasswordResetCode
from .serializers import (
    UserSerializer,
    AdminUserCreateSerializer,
    UserRegistrationSerializer,
    PatientProfileSerializer,
    DoctorProfileSerializer,
    PharmacistProfileSerializer
)
from .permissions import IsPatient, IsDoctor, IsPharmacist, IsAdminUser

RESET_CODE_TTL_MINUTES = 15
RESET_CODE_RESEND_SECONDS = 60
RESET_CODE_MAX_ATTEMPTS = 5


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


class UserListView(generics.ListCreateAPIView):
    """Admin-only list and create of users."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminUserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by("-id")
        role = self.request.query_params.get("role")
        search = self.request.query_params.get("search")
        if role:
            queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(
                email__icontains=search
            ) | queryset.filter(first_name__icontains=search) | queryset.filter(
                last_name__icontains=search
            )
        return queryset

    def perform_create(self, serializer):
        user = serializer.save()
        if user.role == "PATIENT":
            PatientProfile.objects.get_or_create(user=user)
        elif user.role == "DOCTOR":
            DoctorProfile.objects.get_or_create(user=user, defaults={"license_number": f"LIC-{user.id}", "specialization": "General Medicine"})
        elif user.role == "PHARMACIST":
            PharmacistProfile.objects.get_or_create(user=user, defaults={"license_number": f"PHARM-{user.id}", "pharmacy_name": "Central Pharmacy"})


class UserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Admin-only update/detail/delete of a user."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)


def _send_reset_code(user, code):
    send_mail(
        subject=_("Your %(app)s password reset code") % {"app": settings.APP_NAME},
        message=_(
            "Your password reset verification code is: %(code)s\n\n"
            "It expires in %(minutes)s minutes. "
            "If you did not request a password reset, you can ignore this email."
        ) % {"code": code, "minutes": RESET_CODE_TTL_MINUTES},
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


class ForgotPasswordView(generics.GenericAPIView):
    """Email a one-time verification code for a password reset."""

    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()

        # Same response whether or not the account exists (no email enumeration).
        ok_response = Response(
            {
                "message": _(
                    "If an account exists for this email, a verification code has been sent."
                ),
                "expires_in_minutes": RESET_CODE_TTL_MINUTES,
            },
            status=status.HTTP_200_OK,
        )

        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            return ok_response

        now = timezone.now()
        recent = PasswordResetCode.objects.filter(
            user=user,
            used=False,
            created_at__gte=now - timedelta(seconds=RESET_CODE_RESEND_SECONDS),
        ).first()
        if recent:
            retry_after = RESET_CODE_RESEND_SECONDS - int((now - recent.created_at).total_seconds())
            return Response(
                {"message": _("Please wait before requesting a new code."), "retry_after": max(retry_after, 1)},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        PasswordResetCode.objects.filter(user=user, used=False).update(used=True)
        code = f"{secrets.randbelow(1000000):06d}"
        PasswordResetCode.objects.create(
            user=user,
            code=code,
            expires_at=now + timedelta(minutes=RESET_CODE_TTL_MINUTES),
        )

        try:
            _send_reset_code(user, code)
        except Exception:
            return Response(
                {"message": _("We could not send the verification email. Please try again later.")},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return ok_response


class ResetPasswordView(generics.GenericAPIView):
    """Verify the emailed code and set a new password."""

    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data["email"].strip().lower()
        invalid_response = Response(
            {"code": [_("Invalid or expired verification code.")]},
            status=status.HTTP_400_BAD_REQUEST,
        )

        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            return invalid_response

        reset_code = PasswordResetCode.objects.filter(
            user=user, code=data["code"].strip(), used=False
        ).first()
        if reset_code is None:
            # Count the guess against the newest live code so codes can't be brute-forced.
            latest = PasswordResetCode.objects.filter(
                user=user, used=False, expires_at__gt=timezone.now()
            ).first()
            if latest:
                latest.attempts += 1
                if latest.attempts >= RESET_CODE_MAX_ATTEMPTS:
                    latest.used = True
                    latest.save(update_fields=["attempts", "used"])
                else:
                    latest.save(update_fields=["attempts"])
            return invalid_response

        if reset_code.expires_at < timezone.now() or reset_code.attempts >= RESET_CODE_MAX_ATTEMPTS:
            reset_code.used = True
            reset_code.save(update_fields=["used"])
            return invalid_response

        if data["password"] != data["password_confirm"]:
            return Response(
                {"password_confirm": [_("Passwords do not match.")]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(data["password"], user=user)
        except DjangoValidationError as exc:
            return Response({"password": list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        reset_code.used = True
        reset_code.save(update_fields=["used"])

        user.set_password(data["password"])
        user.save(update_fields=["password"])
        PasswordResetCode.objects.filter(user=user, used=False).update(used=True)

        return Response(
            {"message": _("Password reset successfully. You can now sign in.")},
            status=status.HTTP_200_OK,
        )
