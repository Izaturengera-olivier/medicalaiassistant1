"""Tests for the email verification-code password reset flow."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import PasswordResetCode
from accounts.views import RESET_CODE_DAILY_LIMIT, ForgotPasswordBurstThrottle
from core.constants import UserRole

User = get_user_model()


def _create_user(email="reset@example.com", password="OldPass123!"):
    return User.objects.create_user(
        email=email,
        password=password,
        first_name="Res",
        last_name="Et",
        role=UserRole.PATIENT,
    )


@pytest.mark.django_db
class TestForgotPassword:
    def test_sends_code_email(self):
        _create_user()
        response = APIClient().post(
            reverse("forgot_password"), {"email": "reset@example.com"}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["reset@example.com"]
        code = PasswordResetCode.objects.latest("created_at")
        assert code.code in mail.outbox[0].body

    def test_email_is_not_bare_code(self):
        """A near-empty body whose only content is a large code is a phishing
        heuristic, so the message must carry real prose and a Reply-To."""
        _create_user()
        APIClient().post(
            reverse("forgot_password"), {"email": "reset@example.com"}, format="json"
        )
        message = mail.outbox[0]

        assert len(message.body.split()) > 50
        assert message.extra_headers["Auto-Submitted"] == "auto-generated"
        assert message.extra_headers["Reply-To"]
        html = next(body for body, mime in message.alternatives if mime == "text/html")
        assert len(html) > 500

    @override_settings(SUPPORT_EMAIL="support@clinical-cds.test")
    def test_email_advertises_one_click_unsubscribe(self):
        _create_user()
        APIClient().post(
            reverse("forgot_password"), {"email": "reset@example.com"}, format="json"
        )
        headers = mail.outbox[0].extra_headers

        assert headers["List-Unsubscribe"] == (
            "<mailto:support@clinical-cds.test?subject=unsubscribe>"
        )
        assert headers["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"

    def test_daily_limit_caps_sends_per_account(self):
        user = _create_user()
        for i in range(RESET_CODE_DAILY_LIMIT):
            PasswordResetCode.objects.create(
                user=user,
                code=f"{i:06d}",
                expires_at=timezone.now() + timedelta(minutes=1),
                used=True,
            )
        # Backdate past the 60s resend throttle so only the daily cap can fire.
        PasswordResetCode.objects.filter(user=user).update(
            created_at=timezone.now() - timedelta(minutes=10)
        )

        response = APIClient().post(
            reverse("forgot_password"), {"email": "reset@example.com"}, format="json"
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert len(mail.outbox) == 0

    def test_ip_burst_throttle_blocks_repeat_requests(self, monkeypatch):
        # DRF reads THROTTLE_RATES off the class, and test settings null these
        # scopes out so the rest of the suite is unaffected.
        monkeypatch.setattr(
            ForgotPasswordBurstThrottle,
            "THROTTLE_RATES",
            {
                **ForgotPasswordBurstThrottle.THROTTLE_RATES,
                "forgot_password_burst": "2/hour",
            },
        )
        ForgotPasswordBurstThrottle.cache.clear()
        client = APIClient()
        url = reverse("forgot_password")

        # Distinct unknown addresses: the per-account resend throttle can't fire,
        # so any 429 here comes from the IP throttle.
        codes = [
            client.post(url, {"email": f"nobody{i}@example.com"}, format="json").status_code
            for i in range(3)
        ]

        ForgotPasswordBurstThrottle.cache.clear()
        assert codes[:2] == [200, 200]
        assert codes[2] == status.HTTP_429_TOO_MANY_REQUESTS
        assert len(mail.outbox) == 0

    def test_unknown_email_returns_ok_without_sending(self):
        response = APIClient().post(
            reverse("forgot_password"), {"email": "ghost@example.com"}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_resend_is_throttled(self):
        _create_user()
        client = APIClient()
        url = reverse("forgot_password")
        assert client.post(url, {"email": "reset@example.com"}, format="json").status_code == 200
        second = client.post(url, {"email": "reset@example.com"}, format="json")

        assert second.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert len(mail.outbox) == 1

    def test_new_request_invalidates_previous_code(self):
        user = _create_user()
        old = PasswordResetCode.objects.create(
            user=user,
            code="111111",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        # Backdate past the resend throttle window.
        PasswordResetCode.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(minutes=5)
        )
        APIClient().post(
            reverse("forgot_password"), {"email": "reset@example.com"}, format="json"
        )
        old.refresh_from_db()
        assert old.used

    @override_settings(DEBUG=True)
    def test_code_is_never_returned_in_response(self):
        _create_user()
        response = APIClient().post(
            reverse("forgot_password"), {"email": "reset@example.com"}, format="json"
        )
        code = PasswordResetCode.objects.latest("created_at").code

        assert response.status_code == status.HTTP_200_OK
        assert "verification_code" not in response.data
        assert code not in response.content.decode()

    def test_email_failure_returns_502_and_allows_immediate_retry(self, monkeypatch):
        _create_user()
        monkeypatch.setattr("accounts.views._send_reset_code", lambda user, code: False)
        client = APIClient()
        url = reverse("forgot_password")

        first = client.post(url, {"email": "reset@example.com"}, format="json")
        assert first.status_code == status.HTTP_502_BAD_GATEWAY

        # A failed send must not strand the user behind the resend throttle.
        second = client.post(url, {"email": "reset@example.com"}, format="json")
        assert second.status_code == status.HTTP_502_BAD_GATEWAY
        assert len(mail.outbox) == 0


@pytest.mark.django_db
class TestResetPassword:
    def _request_code(self):
        user = _create_user()
        APIClient().post(
            reverse("forgot_password"), {"email": "reset@example.com"}, format="json"
        )
        return user, PasswordResetCode.objects.latest("created_at").code

    def test_reset_success(self):
        _user, code = self._request_code()
        response = APIClient().post(
            reverse("reset_password"),
            {
                "email": "reset@example.com",
                "code": code,
                "password": "NewSecure456!",
                "password_confirm": "NewSecure456!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        user = User.objects.get(email="reset@example.com")
        assert user.check_password("NewSecure456!")
        assert PasswordResetCode.objects.filter(used=False).count() == 0

    def test_wrong_code_rejected(self):
        _user, _code = self._request_code()
        response = APIClient().post(
            reverse("reset_password"),
            {
                "email": "reset@example.com",
                "code": "000000",
                "password": "NewSecure456!",
                "password_confirm": "NewSecure456!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.get(email="reset@example.com").check_password("NewSecure456!")

    def test_code_cannot_be_brute_forced(self):
        _user, code = self._request_code()
        client = APIClient()
        for _ in range(5):
            client.post(
                reverse("reset_password"),
                {
                    "email": "reset@example.com",
                    "code": "000000",
                    "password": "NewSecure456!",
                    "password_confirm": "NewSecure456!",
                },
                format="json",
            )

        response = client.post(
            reverse("reset_password"),
            {
                "email": "reset@example.com",
                "code": code,
                "password": "NewSecure456!",
                "password_confirm": "NewSecure456!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_code_single_use(self):
        _user, code = self._request_code()
        client = APIClient()
        payload = {
            "email": "reset@example.com",
            "code": code,
            "password": "NewSecure456!",
            "password_confirm": "NewSecure456!",
        }
        assert client.post(reverse("reset_password"), payload, format="json").status_code == 200
        assert client.post(reverse("reset_password"), payload, format="json").status_code == 400

    def test_password_mismatch_rejected(self):
        _user, code = self._request_code()
        response = APIClient().post(
            reverse("reset_password"),
            {
                "email": "reset@example.com",
                "code": code,
                "password": "NewSecure456!",
                "password_confirm": "Different789!",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_rejected(self):
        _user, code = self._request_code()
        response = APIClient().post(
            reverse("reset_password"),
            {
                "email": "reset@example.com",
                "code": code,
                "password": "123",
                "password_confirm": "123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_new_password_allows_login(self):
        _user, code = self._request_code()
        client = APIClient()
        client.post(
            reverse("reset_password"),
            {
                "email": "reset@example.com",
                "code": code,
                "password": "NewSecure456!",
                "password_confirm": "NewSecure456!",
            },
            format="json",
        )
        response = client.post(
            reverse("login"),
            {"email": "reset@example.com", "password": "NewSecure456!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
