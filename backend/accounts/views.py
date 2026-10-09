"""HTTP endpoints for accounts. Implemented in later phases."""

import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.utils import timezone
from django.utils.html import escape
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
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

logger = logging.getLogger(__name__)

RESET_CODE_TTL_MINUTES = 15
RESET_CODE_RESEND_SECONDS = 60
RESET_CODE_MAX_ATTEMPTS = 5
# Blasting templated codes from a consumer mailbox is what got this sender
# spam-routed in the first place, so cap the volume per account per day.
RESET_CODE_DAILY_LIMIT = 5


# These must subclass SimpleRateThrottle, not ScopedRateThrottle: the scoped
# variant re-reads `self.scope` from `view.throttle_scope` on every request and
# silently allows everything when the view does not define it.
class _ForgotPasswordThrottle(SimpleRateThrottle):
    """Keyed on client IP. The endpoint is AllowAny, so there is no user to key
    on -- and keying on the target account would let an attacker spread a blast
    across many addresses while staying under every limit."""

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }


class ForgotPasswordBurstThrottle(_ForgotPasswordThrottle):
    scope = "forgot_password_burst"


class ForgotPasswordDailyThrottle(_ForgotPasswordThrottle):
    scope = "forgot_password_daily"


def _create_role_profile(user):
    """Create the role-specific profile for a newly created user.

    license_number is unique and non-null, so it has to be derived from the user
    id. Left to Django's CharField default of "" it collides on the second
    doctor or pharmacist registered, which surfaced as a 500 on /auth/register/.
    """
    if user.role == "PATIENT":
        PatientProfile.objects.get_or_create(user=user)
    elif user.role == "DOCTOR":
        DoctorProfile.objects.get_or_create(
            user=user,
            defaults={
                "license_number": f"LIC-{user.id}",
                "specialization": "General Medicine",
            },
        )
    elif user.role == "PHARMACIST":
        PharmacistProfile.objects.get_or_create(
            user=user,
            defaults={
                "license_number": f"PHARM-{user.id}",
                "pharmacy_name": "Central Pharmacy",
            },
        )


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Atomic so a profile failure cannot leave a user row with no profile.
        with transaction.atomic():
            user = serializer.save()
            _create_role_profile(user)

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
        with transaction.atomic():
            user = serializer.save()
            _create_role_profile(user)


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
    app = settings.APP_NAME
    support = settings.SUPPORT_EMAIL or settings.DEFAULT_FROM_EMAIL
    site_url = settings.SITE_URL
    first_name = user.first_name or _("there")
    recipient = user.email

    subject = _("Reset your %(app)s password") % {"app": app}

    # A near-empty HTML body whose only content is a large code is one of the
    # strongest phishing heuristics, so both parts carry real sentences that
    # say who sent it, why, what to do, and what happens if it was a mistake.
    greeting = _("Hi %(name)s,") % {"name": first_name}
    requested = _(
        "Someone requested a password reset for the %(app)s account signed in as "
        "%(email)s."
    ) % {"app": app, "email": recipient}
    prompt = _("Your verification code is:")
    expiry = _(
        "It expires in %(minutes)s minutes and can be used only once. Enter it in "
        "%(app)s to choose a new password."
    ) % {"minutes": RESET_CODE_TTL_MINUTES, "app": app}
    not_you = _(
        "If you did not request this, you can safely ignore this email. Your "
        "password will not change, and the code above cannot be used without it."
    )
    help_line = _("Need help? Email %(support)s.") % {"support": support}
    why_line = _(
        "You are receiving this email because a password reset was requested for "
        "your %(app)s account."
    ) % {"app": app}

    text_body = "\n\n".join(
        str(part)
        for part in [
            greeting,
            requested,
            f"{prompt}\n\n    {code}",
            expiry,
            not_you,
            "\n".join(
                str(line)
                for line in filter(
                    None,
                    [
                        "--",
                        app,
                        site_url,
                        help_line,
                        "",
                        why_line,
                    ],
                )
            ),
        ]
    )

    safe = {
        "app": escape(app),
        "code": escape(code),
        "name": escape(first_name),
        "email": escape(recipient),
        "support": escape(support),
        "site_url": escape(site_url),
        "greeting": escape(greeting),
        "requested": escape(requested),
        "prompt": escape(prompt),
        "expiry": escape(expiry),
        "not_you": escape(not_you),
        "help_line": escape(help_line),
        "why_line": escape(why_line),
    }
    site_html = (
        f"<a href='{safe['site_url']}' style='color:#0d9488'>{safe['site_url']}</a>"
        if site_url
        else ""
    )
    html_body = f"""<!doctype html>
<html><body style="margin:0;padding:0;background:#f1f5f9">
<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
     font-size:15px;line-height:1.6;color:#0f172a;background:#f1f5f9;padding:24px">
  <div style="max-width:520px;margin:0 auto;background:#ffffff;border-radius:12px;
       border:1px solid #e2e8f0;overflow:hidden">
    <div style="padding:20px 28px;border-bottom:1px solid #e2e8f0">
      <span style="font-size:16px;font-weight:700;color:#0f766e">{safe['app']}</span>
    </div>
    <div style="padding:28px">
      <p style="margin:0 0 16px">{safe['greeting']}</p>
      <p style="margin:0 0 20px">{safe['requested']}</p>
      <p style="margin:0 0 8px">{safe['prompt']}</p>
      <p style="margin:0 0 20px;padding:16px;background:#f0fdfa;border:1px solid #99f6e4;
         border-radius:8px;font-size:28px;font-weight:700;letter-spacing:6px;
         color:#0f766e;text-align:center">{safe['code']}</p>
      <p style="margin:0 0 16px">{safe['expiry']}</p>
      <p style="margin:0 0 8px;color:#475569">{safe['not_you']}</p>
      <p style="margin:0;color:#475569">{safe['help_line']}</p>
    </div>
    <div style="padding:20px 28px;background:#f8fafc;border-top:1px solid #e2e8f0;
         font-size:12px;color:#64748b">
      <p style="margin:0 0 6px">{safe['why_line']}</p>
      <p style="margin:0">{safe['app']}{('&nbsp;&middot;&nbsp;' + site_html) if site_url else ''}</p>
    </div>
  </div>
</div>
</body></html>"""

    headers = {
        # Stops mailers from replying to this with an out-of-office message.
        "Auto-Submitted": "auto-generated",
        "Reply-To": support,
        # Priority headers - indicate this is transactional, not bulk email
        "X-Priority": "3",
        "X-MSMail-Priority": "Normal",
        "X-Mailer": f"{app} Password Reset",
        # Precedence helps prevent auto-replies
        "Precedence": "bulk",
    }
    if settings.SUPPORT_EMAIL:
        # Gmail and Yahoo treat a working unsubscribe route as a trust signal.
        headers["List-Unsubscribe"] = f"<mailto:{support}?subject=unsubscribe>"
        headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=f"{app} <{settings.DEFAULT_FROM_EMAIL}>",
            to=[recipient],
            headers=headers,
        )
        message.attach_alternative(html_body, "text/html")
        message.send()
        return True
    except Exception:
        # Never log the code itself; logs get aggregated and shipped around.
        logger.exception("Password reset email to %s failed", user.email)
        return False


class ForgotPasswordView(generics.GenericAPIView):
    """Email a one-time verification code for a password reset."""

    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]
    # Unauthenticated and mail-sending, so without these anyone could use this
    # endpoint to burn the sender's reputation.
    throttle_classes = [ForgotPasswordBurstThrottle, ForgotPasswordDailyThrottle]

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

        sent_today = PasswordResetCode.objects.filter(
            user=user, created_at__gte=now - timedelta(days=1)
        ).count()
        if sent_today >= RESET_CODE_DAILY_LIMIT:
            return Response(
                {
                    "message": _(
                        "This account has requested too many codes today. "
                        "Try again tomorrow or contact support."
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        PasswordResetCode.objects.filter(user=user, used=False).update(used=True)
        code = f"{secrets.randbelow(1000000):06d}"
        reset_code = PasswordResetCode.objects.create(
            user=user,
            code=code,
            expires_at=now + timedelta(minutes=RESET_CODE_TTL_MINUTES),
        )

        if not _send_reset_code(user, code):
            # Without this the code sits in the DB unused and blocks the resend
            # throttle, so a user whose email failed can't retry for a minute.
            reset_code.used = True
            reset_code.save(update_fields=["used"])
            return Response(
                {
                    "message": _(
                        "We could not send the verification email. Please try again later."
                    )
                },
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
