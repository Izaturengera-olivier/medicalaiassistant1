"""
Constants for the Clinical Decision Support system.
"""

# User Roles
class UserRole:
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    PHARMACIST = "PHARMACIST"
    ADMIN = "ADMIN"
    
    CHOICES = [
        (PATIENT, "Patient"),
        (DOCTOR, "Doctor"),
        (PHARMACIST, "Pharmacist"),
        (ADMIN, "Admin"),
    ]


# Consultation Status
class ConsultationStatus:
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    
    CHOICES = [
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]


# Urgency Levels
class UrgencyLevel:
    INFORMATIONAL = "INFORMATIONAL"
    ROUTINE_CONSULTATION = "ROUTINE_CONSULTATION"
    PROMPT_MEDICAL_REVIEW = "PROMPT_MEDICAL_REVIEW"
    URGENT_MEDICAL_ATTENTION = "URGENT_MEDICAL_ATTENTION"
    
    CHOICES = [
        (INFORMATIONAL, "Informational"),
        (ROUTINE_CONSULTATION, "Routine Consultation"),
        (PROMPT_MEDICAL_REVIEW, "Prompt Medical Review"),
        (URGENT_MEDICAL_ATTENTION, "Urgent Medical Attention"),
    ]


# AI Suggestion Actions
class AISuggestionAction:
    ACCEPT = "ACCEPT"
    MODIFY = "MODIFY"
    REJECT = "REJECT"
    
    CHOICES = [
        (ACCEPT, "Accept"),
        (MODIFY, "Modify"),
        (REJECT, "Reject"),
    ]


# Prescription Status
class PrescriptionStatus:
    ACTIVE = "ACTIVE"
    DISCONTINUED = "DISCONTINUED"
    COMPLETED = "COMPLETED"
    
    CHOICES = [
        (ACTIVE, "Active"),
        (DISCONTINUED, "Discontinued"),
        (COMPLETED, "Completed"),
    ]


# Source Types
class SourceType:
    WHO = "WHO"
    MOH = "MOH"  # Ministry of Health
    FDA = "FDA"
    HOSPITAL = "HOSPITAL"
    LITERATURE = "LITERATURE"
    GUIDELINE = "GUIDELINE"
    
    CHOICES = [
        (WHO, "WHO"),
        (MOH, "Ministry of Health"),
        (FDA, "FDA"),
        (HOSPITAL, "Hospital"),
        (LITERATURE, "Literature"),
        (GUIDELINE, "Guideline"),
    ]


# Interaction Severity
class InteractionSeverity:
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    CONTRAINDICATED = "CONTRAINDICATED"
    
    CHOICES = [
        (MILD, "Mild"),
        (MODERATE, "Moderate"),
        (SEVERE, "Severe"),
        (CONTRAINDICATED, "Contraindicated"),
    ]
