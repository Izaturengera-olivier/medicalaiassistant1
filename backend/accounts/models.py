"""Domain models for accounts. Implemented in Phase 2.

User accounts, roles, JWT-facing identity.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import UserRole


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email-based authentication and roles."""

    username = None  # Remove username field
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.PATIENT,
        help_text=_("User role in the system")
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    is_verified = models.BooleanField(
        _("verified"),
        default=False,
        help_text=_("Whether the user email has been verified")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def get_full_name(self):
        """Return the full name for the user."""
        return f"{self.first_name} {self.last_name}".strip()

    def is_patient(self):
        """Check if user is a patient."""
        return self.role == UserRole.PATIENT

    def is_doctor(self):
        """Check if user is a doctor."""
        return self.role == UserRole.DOCTOR

    def is_pharmacist(self):
        """Check if user is a pharmacist."""
        return self.role == UserRole.PHARMACIST

    def is_admin_user(self):
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN


class PatientProfile(models.Model):
    """Extended profile for patient users."""

    GENDER_CHOICES = [
        ("M", _("Male")),
        ("F", _("Female")),
        ("O", _("Other")),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        verbose_name=_("user")
    )
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("gender")
    )
    phone = models.CharField(_("phone number"), max_length=20, blank=True)
    address = models.TextField(_("address"), blank=True)
    emergency_contact_name = models.CharField(
        _("emergency contact name"),
        max_length=200,
        blank=True
    )
    emergency_contact_phone = models.CharField(
        _("emergency contact phone"),
        max_length=20,
        blank=True
    )
    blood_type = models.CharField(
        _("blood type"),
        max_length=5,
        blank=True,
        help_text=_("e.g., A+, B-, O+, etc.")
    )
    allergies = models.JSONField(
        _("allergies"),
        default=list,
        blank=True,
        help_text=_("List of known allergies")
    )
    chronic_conditions = models.JSONField(
        _("chronic conditions"),
        default=list,
        blank=True,
        help_text=_("List of chronic conditions")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "patient_profiles"
        verbose_name = _("patient profile")
        verbose_name_plural = _("patient profiles")

    def __str__(self):
        return f"Patient Profile: {self.user.get_full_name()}"


class DoctorProfile(models.Model):
    """Extended profile for doctor users."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        verbose_name=_("user")
    )
    license_number = models.CharField(
        _("license number"),
        max_length=100,
        unique=True,
        help_text=_("Medical license number")
    )
    specialization = models.CharField(
        _("specialization"),
        max_length=200,
        help_text=_("Medical specialization")
    )
    hospital_or_clinic = models.CharField(
        _("hospital/clinic"),
        max_length=300,
        blank=True,
        help_text=_("Name of hospital or clinic")
    )
    years_of_experience = models.PositiveIntegerField(
        _("years of experience"),
        default=0,
        help_text=_("Years of medical experience")
    )
    verified = models.BooleanField(
        _("verified"),
        default=False,
        help_text=_("Whether the doctor's credentials have been verified")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_profiles"
        verbose_name = _("doctor profile")
        verbose_name_plural = _("doctor profiles")

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"


class PharmacistProfile(models.Model):
    """Extended profile for pharmacist users."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pharmacist_profile",
        verbose_name=_("user")
    )
    license_number = models.CharField(
        _("license number"),
        max_length=100,
        unique=True,
        help_text=_("Pharmacy license number")
    )
    pharmacy_name = models.CharField(
        _("pharmacy name"),
        max_length=300,
        help_text=_("Name of pharmacy")
    )
    pharmacy_location = models.CharField(
        _("pharmacy location"),
        max_length=300,
        blank=True,
        help_text=_("Physical location of pharmacy")
    )
    verified = models.BooleanField(
        _("verified"),
        default=False,
        help_text=_("Whether the pharmacist's credentials have been verified")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pharmacist_profiles"
        verbose_name = _("pharmacist profile")
        verbose_name_plural = _("pharmacist profiles")

    def __str__(self):
        return f"Pharmacist {self.user.get_full_name()} - {self.pharmacy_name}"
