"""Object-level and role permissions for accounts. Phase 3+."""

from rest_framework import permissions
from django.utils.translation import gettext_lazy as _

from core.constants import UserRole


class IsPatient(permissions.BasePermission):
    """Permission to only allow patients to access the view."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.PATIENT


class IsDoctor(permissions.BasePermission):
    """Permission to only allow doctors to access the view."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.DOCTOR


class IsPharmacist(permissions.BasePermission):
    """Permission to only allow pharmacists to access the view."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.PHARMACIST


class IsAdminUser(permissions.BasePermission):
    """Permission to only allow admin users to access the view."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsPatientOwner(permissions.BasePermission):
    """Permission to only allow patients to access their own data."""

    def has_object_permission(self, request, view, obj):
        return obj.patient == request.user


class IsAssignedDoctor(permissions.BasePermission):
    """Permission to only allow assigned doctors to access consultation data."""

    def has_object_permission(self, request, view, obj):
        return obj.assigned_doctor == request.user or request.user.is_staff


class IsVerifiedHealthcareProfessional(permissions.BasePermission):
    """Permission to only allow verified healthcare professionals."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role == UserRole.DOCTOR:
            return hasattr(request.user, 'doctor_profile') and request.user.doctor_profile.verified
        elif request.user.role == UserRole.PHARMACIST:
            return hasattr(request.user, 'pharmacist_profile') and request.user.pharmacist_profile.verified
        
        return False


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """Permission to allow safe methods to authenticated users, and write methods only to admin users."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == UserRole.ADMIN

