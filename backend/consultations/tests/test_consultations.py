"""Tests for consultation system."""

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.constants import UserRole, ConsultationStatus

from consultations.models import Consultation, Symptom, PatientSymptom
from accounts.models import PatientProfile
from patients.models import MedicalHistory

User = get_user_model()


@pytest.mark.django_db
class TestConsultationAPI:
    """Test consultation API endpoints."""

    def test_create_consultation_as_patient(self):
        """Test that patients can create consultations."""
        user = User.objects.create_user(
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = "/api/consultations/consultations/"
        data = {"chief_complaint": "I have a headache and fever"}
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Consultation.objects.filter(patient=user).exists()
        consultation = Consultation.objects.get(patient=user)
        assert consultation.chief_complaint == "I have a headache and fever"
        # Clients need the new id to keep talking to the same consultation.
        assert response.data["id"] == consultation.id

    def test_list_consultations_as_patient(self):
        """Test that patients can only see their own consultations."""
        user = User.objects.create_user(
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=user)
        
        # Create consultation for this user
        consultation = Consultation.objects.create(
            patient=user,
            chief_complaint="Headache"
        )
        
        # Create consultation for another user
        other_user = User.objects.create_user(
            email="other@example.com",
            first_name="Other",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=other_user)
        Consultation.objects.create(
            patient=other_user,
            chief_complaint="Fever"
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = "/api/consultations/consultations/"
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == consultation.id

    def test_update_consultation_status_as_doctor(self):
        """Test that doctors can update consultation status."""
        patient = User.objects.create_user(
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=patient)
        
        doctor = User.objects.create_user(
            email="doctor@example.com",
            first_name="Jane",
            last_name="Smith",
            role=UserRole.DOCTOR,
            password="SecurePass123!"
        )
        
        consultation = Consultation.objects.create(
            patient=patient,
            chief_complaint="Headache",
            assigned_doctor=doctor
        )
        
        client = APIClient()
        client.force_authenticate(user=doctor)
        
        url = f"/api/consultations/consultations/{consultation.id}/"
        data = {"status": ConsultationStatus.COMPLETED}
        
        response = client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        consultation.refresh_from_db()
        assert consultation.status == ConsultationStatus.COMPLETED

    def test_patient_cannot_update_other_consultation(self):
        """Test that patients cannot update consultations they don't own."""
        patient1 = User.objects.create_user(
            email="patient1@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=patient1)
        
        patient2 = User.objects.create_user(
            email="patient2@example.com",
            first_name="Jane",
            last_name="Smith",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=patient2)
        
        consultation = Consultation.objects.create(
            patient=patient2,
            chief_complaint="Headache"
        )
        
        client = APIClient()
        client.force_authenticate(user=patient1)
        
        url = f"/api/consultations/consultations/{consultation.id}/"
        data = {"chief_complaint": "Modified complaint"}
        
        response = client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestSymptomAPI:
    """Test symptom API endpoints."""

    def test_list_symptoms(self):
        """Test listing symptoms."""
        Symptom.objects.create(name="Headache", category="neurological")
        Symptom.objects.create(name="Fever", category="general")
        
        client = APIClient()
        user = User.objects.create_user(
            email="user@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        client.force_authenticate(user=user)
        
        url = "/api/consultations/symptoms/"
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_add_patient_symptom(self):
        """Test adding a symptom to a consultation."""
        patient = User.objects.create_user(
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=patient)
        
        consultation = Consultation.objects.create(
            patient=patient,
            chief_complaint="Headache"
        )
        
        symptom = Symptom.objects.create(name="Headache", category="neurological")
        
        client = APIClient()
        client.force_authenticate(user=patient)
        
        url = "/api/consultations/patient-symptoms/"
        data = {
            "consultation": consultation.id,
            "symptom_id": symptom.id,
            "severity": "moderate",
            "duration": "2 days"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert PatientSymptom.objects.filter(consultation=consultation, symptom=symptom).exists()


@pytest.mark.django_db
class TestMedicalHistoryAPI:
    """Test medical history API endpoints."""

    def test_create_medical_history(self):
        """Test creating medical history."""
        patient = User.objects.create_user(
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=patient)
        
        client = APIClient()
        client.force_authenticate(user=patient)
        
        url = "/api/patients/medical-history/"
        data = {
            "condition_name": "Hypertension",
            "diagnosis_date": "2024-01-15",
            "notes": "Controlled with medication"
        }
        
        response = client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert MedicalHistory.objects.filter(patient=patient, condition_name="Hypertension").exists()

    def test_list_medical_history_as_patient(self):
        """Test that patients can see their own medical history."""
        patient = User.objects.create_user(
            email="patient@example.com",
            first_name="John",
            last_name="Doe",
            role=UserRole.PATIENT,
            password="SecurePass123!"
        )
        PatientProfile.objects.create(user=patient)
        
        from patients.models import MedicalHistory
        MedicalHistory.objects.create(
            patient=patient,
            condition_name="Hypertension",
            diagnosis_date="2024-01-15"
        )
        
        client = APIClient()
        client.force_authenticate(user=patient)
        
        url = "/api/patients/medical-history/"
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["condition_name"] == "Hypertension"