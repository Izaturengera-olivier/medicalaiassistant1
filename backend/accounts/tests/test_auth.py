"""Tests for authentication and authorization."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.constants import UserRole

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration endpoint."""

    def test_register_patient_success(self):
        """Test successful patient registration."""
        client = APIClient()
        url = reverse("register")
        data = {
            "email": "patient@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.PATIENT,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="patient@example.com").exists()
        assert response.data["user"]["email"] == "patient@example.com"
        assert response.data["user"]["role"] == UserRole.PATIENT

    def test_register_doctor_success(self):
        """Test successful doctor registration."""
        client = APIClient()
        url = reverse("register")
        data = {
            "email": "doctor@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "role": UserRole.DOCTOR,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="doctor@example.com").exists()
        assert response.data["user"]["role"] == UserRole.DOCTOR

    def test_register_password_mismatch(self):
        """Test registration with password mismatch."""
        client = APIClient()
        url = reverse("register")
        data = {
            "email": "patient@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.PATIENT,
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        User.objects.create_user(
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        
        client = APIClient()
        url = reverse("register")
        data = {
            "email": "existing@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.PATIENT,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Test user login endpoint."""

    def test_login_success(self):
        """Test successful login."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        
        client = APIClient()
        url = reverse("login")
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert response.data["user"]["email"] == "test@example.com"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        
        client = APIClient()
        url = reverse("login")
        data = {
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """Test token refresh endpoint."""

    def test_token_refresh_success(self):
        """Test successful token refresh."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        
        client = APIClient()
        
        # First, login to get tokens
        login_url = reverse("login")
        login_data = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        login_response = client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["refresh"]
        
        # Then, refresh the token
        refresh_url = reverse("token_refresh")
        refresh_data = {"refresh": refresh_token}
        refresh_response = client.post(refresh_url, refresh_data, format="json")
        
        assert refresh_response.status_code == status.HTTP_200_OK
        assert "access" in refresh_response.data


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile endpoints."""

    def test_get_user_me_authenticated(self):
        """Test getting current user info when authenticated."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse("user_me")
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "test@example.com"

    def test_get_user_me_unauthenticated(self):
        """Test getting current user info when not authenticated."""
        client = APIClient()
        
        url = reverse("user_me")
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile(self):
        """Test updating user profile."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse("user_profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.last_name == "Name"


@pytest.mark.django_db
class TestRoleBasedPermissions:
    """Test role-based permissions."""

    def test_patient_can_access_patient_profile(self):
        """Test that patients can access their own profile."""
        user = User.objects.create_user(
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        
        # Create patient profile
        from accounts.models import PatientProfile
        PatientProfile.objects.create(user=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse("patient_profile")
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_doctor_cannot_access_patient_profile(self):
        """Test that doctors cannot access patient profile endpoint."""
        user = User.objects.create_user(
            email="doctor@example.com",
            first_name="Jane",
            last_name="Smith",
            role=UserRole.DOCTOR,
            password="SecurePass123!"
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse("patient_profile")
        response = client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_access_all_endpoints(self):
        """Test that admin users have broader access."""
        user = User.objects.create_user(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            password="SecurePass123!",
            is_staff=True
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse("user_me")
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK