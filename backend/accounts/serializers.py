"""DRF serializers for accounts. Implemented with APIs in later phases."""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from core.constants import UserRole
from .models import User, PatientProfile, DoctorProfile, PharmacistProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "is_verified", "created_at", "updated_at"]
        read_only_fields = ["id", "is_verified", "created_at", "updated_at"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "password", "password_confirm"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": _("Password fields didn't match.")})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for PatientProfile."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "user", "date_of_birth", "gender", "phone", "address",
            "emergency_contact_name", "emergency_contact_phone",
            "blood_type", "allergies", "chronic_conditions"
        ]


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for DoctorProfile."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "user", "license_number", "specialization", "hospital_or_clinic",
            "years_of_experience", "verified"
        ]


class PharmacistProfileSerializer(serializers.ModelSerializer):
    """Serializer for PharmacistProfile."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = PharmacistProfile
        fields = [
            "user", "license_number", "pharmacy_name", "pharmacy_location", "verified"
        ]
