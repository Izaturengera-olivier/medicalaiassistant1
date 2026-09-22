"""Service for medical triage and urgency assessment."""

from typing import Dict, List, Any
from django.utils.translation import gettext_lazy as _

from core.constants import UrgencyLevel


class TriageService:
    """Service for determining medical urgency and triage recommendations."""

    # Emergency indicators requiring immediate attention
    EMERGENCY_INDICATORS = [
        "chest pain", "heart attack", "stroke", "difficulty breathing",
        "shortness of breath", "severe bleeding", "loss of consciousness",
        "confusion", "slurred speech", "sudden weakness", "severe headache",
        "suicidal thoughts", "self harm", "severe trauma", "anaphylaxis"
    ]

    # Urgent indicators requiring prompt attention
    URGENT_INDICATORS = [
        "high fever", "severe pain", "persistent vomiting", "dehydration",
        "severe diarrhea", "infection signs", "worsening symptoms",
        "difficulty swallowing", "severe allergic reaction"
    ]

    # Routine indicators
    ROUTINE_INDICATORS = [
        "mild pain", "mild fever", "cough", "cold symptoms",
        "mild fatigue", "minor injury", "routine checkup"
    ]

    @classmethod
    def assess_urgency(cls, symptoms: List[str], patient_input: str) -> str:
        """
        Assess the urgency level based on symptoms and patient input.
        
        Args:
            symptoms: List of identified symptoms
            patient_input: Original patient description
            
        Returns:
            Urgency level constant
        """
        text_lower = patient_input.lower()
        
        # Check for emergency indicators first
        for indicator in cls.EMERGENCY_INDICATORS:
            if indicator in text_lower:
                return UrgencyLevel.URGENT_MEDICAL_ATTENTION
        
        # Check for urgent indicators
        for indicator in cls.URGENT_INDICATORS:
            if indicator in text_lower:
                return UrgencyLevel.PROMPT_MEDICAL_REVIEW
        
        # Check for routine indicators
        for indicator in cls.ROUTINE_INDICATORS:
            if indicator in text_lower:
                return UrgencyLevel.ROUTINE_CONSULTATION
        
        # Default to routine consultation if no specific indicators found
        return UrgencyLevel.ROUTINE_CONSULTATION

    @classmethod
    def get_triage_recommendation(cls, urgency_level: str) -> Dict[str, Any]:
        """
        Get triage recommendation based on urgency level.
        
        Args:
            urgency_level: The assessed urgency level
            
        Returns:
            Dictionary with recommendation details
        """
        recommendations = {
            UrgencyLevel.INFORMATIONAL: {
                "action": "Self-monitor",
                "timeframe": "Monitor symptoms",
                "description": "Monitor your symptoms and maintain good hydration. Consult a healthcare provider if symptoms persist or worsen.",
                "follow_up": "Consult within 1-2 weeks if no improvement"
            },
            UrgencyLevel.ROUTINE_CONSULTATION: {
                "action": "Schedule appointment",
                "timeframe": "Within 3-5 days",
                "description": "Schedule an appointment with your healthcare provider within the next few days for proper evaluation and treatment.",
                "follow_up": "Follow up with primary care provider"
            },
            UrgencyLevel.PROMPT_MEDICAL_REVIEW: {
                "action": "Seek medical attention",
                "timeframe": "Within 24 hours",
                "description": "Seek medical attention within 24 hours for proper evaluation and treatment. Do not wait for symptoms to worsen.",
                "follow_up": "Urgent care or primary care same-day appointment"
            },
            UrgencyLevel.URGENT_MEDICAL_ATTENTION: {
                "action": "Emergency care",
                "timeframe": "Immediately",
                "description": "Seek immediate medical attention. Call emergency services (911 or local emergency number) or go to the nearest emergency room.",
                "follow_up": "Emergency department or call emergency services"
            }
        }
        
        return recommendations.get(urgency_level, recommendations[UrgencyLevel.ROUTINE_CONSULTATION])

    @classmethod
    def identify_warning_signs(cls, patient_input: str, symptoms: List[str]) -> List[str]:
        """
        Identify warning signs that require immediate attention.
        
        Args:
            patient_input: Patient's description
            symptoms: Identified symptoms
            
        Returns:
            List of warning signs
        """
        warning_signs = []
        text_lower = patient_input.lower()
        
        # Check for emergency indicators
        for indicator in cls.EMERGENCY_INDICATORS:
            if indicator in text_lower:
                warning_signs.append(indicator.replace("_", " ").capitalize())
        
        # Check for severe symptoms
        severe_patterns = ["severe", "extreme", "unbearable", "worst ever"]
        for pattern in severe_patterns:
            if pattern in text_lower:
                for symptom in symptoms:
                    warning_signs.append(f"Severe {symptom}")
        
        return warning_signs

    @classmethod
    def generate_disclaimer(cls) -> str:
        """Generate medical disclaimer for AI assessments."""
        return """
        IMPORTANT MEDICAL DISCLAIMER:
        This system provides decision-support information only and is not a substitute for professional medical advice, diagnosis, or treatment.
        
        - This assessment is based on the information provided and may not capture all relevant factors
        - AI assessments should be reviewed by qualified healthcare professionals
        - Final diagnosis, prescription, and treatment decisions remain the responsibility of healthcare professionals
        - If you experience severe symptoms or emergency warning signs, seek immediate medical attention
        - This system does not provide emergency medical services
        
        Always consult with qualified healthcare professionals for medical concerns.
        """