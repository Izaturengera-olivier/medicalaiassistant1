"""Admin registrations for accounts. Populated in later phases."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, PatientProfile, DoctorProfile, PharmacistProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    list_display = ["email", "first_name", "last_name", "role", "is_verified", "is_active", "created_at"]
    list_filter = ["role", "is_verified", "is_active", "created_at"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "role")}),
        (_("Permissions"), {"fields": ("is_active", "is_verified", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Admin interface for PatientProfile."""

    list_display = ["user", "date_of_birth", "gender", "phone", "blood_type"]
    list_filter = ["gender", "blood_type"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    """Admin interface for DoctorProfile."""

    list_display = ["user", "license_number", "specialization", "hospital_or_clinic", "verified"]
    list_filter = ["verified", "specialization"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "license_number", "specialization"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PharmacistProfile)
class PharmacistProfileAdmin(admin.ModelAdmin):
    """Admin interface for PharmacistProfile."""

    list_display = ["user", "license_number", "pharmacy_name", "pharmacy_location", "verified"]
    list_filter = ["verified"]
    search_fields = ["user__email", "user__first_name", "user__last_name", "license_number", "pharmacy_name"]
    readonly_fields = ["created_at", "updated_at"]
