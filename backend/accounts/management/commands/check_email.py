"""Send a test email and print what the provider actually said.

A 250 from a relay means "accepted for delivery", not "landed in the inbox".
Gmail in particular accepts mail at RCPT TO time for addresses it discards
later, so this prints the transcript and the latency instead of a bare
success flag -- a sub-100ms "success" means nothing was sent at all.
"""

import smtplib
import time

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send a password-reset-style test email and show the SMTP conversation."

    def add_arguments(self, parser):
        parser.add_argument("to_email", help="Destination inbox you can actually open.")
        parser.add_argument(
            "--no-transcript",
            action="store_true",
            help="Skip the raw SMTP conversation.",
        )

    def _describe_config(self):
        backend = settings.EMAIL_BACKEND
        self.stdout.write("Active email configuration")
        self.stdout.write(f"  EMAIL_BACKEND      : {backend}")
        self.stdout.write(f"  EMAIL_HOST         : {settings.EMAIL_HOST or '(unset)'}")
        self.stdout.write(f"  EMAIL_PORT         : {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS      : {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_HOST_USER    : {settings.EMAIL_HOST_USER or '(unset)'}")
        self.stdout.write(
            f"  EMAIL_HOST_PASSWORD: {'set (%d chars)' % len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(unset)'}"
        )
        self.stdout.write(f"  DEFAULT_FROM_EMAIL : {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write("")

        if "console" in backend:
            self.stderr.write(
                "CONSOLE BACKEND ACTIVE - no email will ever reach an inbox. "
                "Set both EMAIL_HOST and EMAIL_HOST_PASSWORD in .env, then restart "
                "runserver (Django's autoreloader ignores .env changes)."
            )
            return False
        return True

    def handle(self, *args, **options):
        to_email = options["to_email"]
        self._describe_config()

        message = EmailMultiAlternatives(
            subject="Clinical CDS email delivery test",
            body=(
                "This is a delivery test from the Clinical CDS backend.\n"
                "If you can read this, SMTP delivery to your inbox works.\n"
            ),
            from_email=f"{settings.APP_NAME} <{settings.DEFAULT_FROM_EMAIL}>",
            to=[to_email],
        )
        message.attach_alternative(
            "<p><strong>Clinical CDS delivery test.</strong> "
            "If you can read this, SMTP delivery to your inbox works.</p>",
            "text/html",
        )

        patched = None
        if not options["no_transcript"] and "smtp" in settings.EMAIL_BACKEND:
            original = smtplib.SMTP

            class TracingSMTP(original):
                def __init__(self, *a, **kwargs):
                    super().__init__(*a, **kwargs)
                    self.set_debuglevel(2)

            patched = original
            smtplib.SMTP = TracingSMTP

        self.stdout.write(f"Sending to {to_email} ...")
        started = time.time()
        try:
            message.send()
        except Exception as exc:
            elapsed = time.time() - started
            self.stderr.write("")
            self.stderr.write(
                f"FAILED after {elapsed:.2f}s: {type(exc).__name__}: {exc}"
            )
            self.stderr.write(
                "The provider rejected the message. Nothing was delivered."
            )
            raise SystemExit(1)
        finally:
            if patched is not None:
                smtplib.SMTP = patched

        elapsed = time.time() - started
        self.stdout.write("")
        self.stdout.write(f"Accepted by the relay in {elapsed:.2f}s.")

        if elapsed < 0.1:
            self.stderr.write(
                "Suspiciously fast - no TLS handshake happened. "
                "Check that the SMTP backend is really active."
            )

        self.stdout.write(
            "Acceptance is NOT delivery. Now check the destination inbox:\n"
            "  1. Inbox, then Spam, then 'All Mail' (Gmail filters are separate).\n"
            "  2. Search for the exact subject above.\n"
            "  3. If absent from all three, the provider is discarding it "
            "post-acceptance - that is a sender-reputation or "
            "SPF/DKIM-alignment problem, not an application bug."
        )
