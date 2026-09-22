"""AI Service for medical assessments and consultations."""

import json
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.exceptions import AIServiceError
from .prompts import get_system_prompt, get_assessment_prompt


class AIService:
    """Service for AI-powered medical assessments."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL

    def analyze_symptoms(
        self,
        patient_input: str,
        patient_history: Optional[Dict] = None,
        current_medications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze patient symptoms and generate structured assessment.
        
        Args:
            patient_input: Natural language description of symptoms
            patient_history: Patient's medical history
            current_medications: List of current medications
            
        Returns:
            Structured AI assessment
        """
        try:
            if self.provider == "mock":
                return self._mock_analysis(patient_input, patient_history, current_medications)
            else:
                # For real implementation, this would be async
                # For now, return mock
                return self._mock_analysis(patient_input, patient_history, current_medications)
        except Exception as e:
            raise AIServiceError(f"AI analysis failed: {str(e)}")

    def generate_follow_up_questions(
        self,
        consultation_context: Dict,
        current_symptoms: List[str]
    ) -> List[str]:
        """
        Generate follow-up questions based on current information.
        
        Args:
            consultation_context: Current consultation information
            current_symptoms: Symptoms already identified
            
        Returns:
            List of follow-up questions
        """
        try:
            if self.provider == "mock":
                return self._mock_follow_up_questions(current_symptoms)
            else:
                # For real implementation, this would be async
                return self._mock_follow_up_questions(current_symptoms)
        except Exception as e:
            raise AIServiceError(f"Follow-up question generation failed: {str(e)}")

    def _mock_analysis(
        self,
        patient_input: str,
        patient_history: Optional[Dict] = None,
        current_medications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock AI analysis for development/testing."""
        
        # Extract symptoms from input (simple keyword matching)
        symptoms = self._extract_symptoms_from_text(patient_input)
        
        # Generate follow-up questions
        follow_up_questions = self._mock_follow_up_questions(symptoms)
        
        # Determine urgency level
        urgency_level = self._determine_urgency(patient_input, symptoms)
        
        # Identify possible conditions (mock)
        possible_conditions = self._mock_possible_conditions(symptoms)
        
        # Check for warning signs
        warning_signs = self._check_warning_signs(patient_input, symptoms)
        
        return {
            "symptoms_identified": symptoms,
            "follow_up_questions": follow_up_questions,
            "possible_conditions": possible_conditions,
            "warning_signs": warning_signs,
            "urgency_level": urgency_level,
            "general_information": self._generate_general_information(symptoms),
            "medication_information": [],
            "recommended_next_step": self._generate_recommendation(urgency_level),
            "sources": [
                {
                    "name": "WHO",
                    "url": "https://www.who.int",
                    "title": "World Health Organization"
                }
            ],
            "model_used": "mock",
            "confidence": 0.7
        }

    def _real_analysis(
        self,
        patient_input: str,
        patient_history: Optional[Dict] = None,
        current_medications: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Real AI analysis using configured LLM provider."""
        # This will be implemented with actual LLM API calls
        # For now, fall back to mock
        return self._mock_analysis(patient_input, patient_history, current_medications)

    def _real_follow_up_questions(
        self,
        consultation_context: Dict,
        current_symptoms: List[str]
    ) -> List[str]:
        """Real follow-up question generation using LLM."""
        # This will be implemented with actual LLM API calls
        return self._mock_follow_up_questions(current_symptoms)

    def _extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract symptoms from natural language text (simple implementation)."""
        # Common symptom keywords
        symptom_keywords = [
            "headache", "fever", "cough", "body pain", "stomach pain",
            "nausea", "vomiting", "diarrhea", "fatigue", "dizziness",
            "chest pain", "shortness of breath", "sore throat", "runny nose"
        ]
        
        text_lower = text.lower()
        found_symptoms = []
        
        for keyword in symptom_keywords:
            if keyword in text_lower:
                found_symptoms.append(keyword.capitalize())
        
        return found_symptoms

    def _mock_follow_up_questions(self, symptoms: List[str]) -> List[str]:
        """Generate mock follow-up questions based on symptoms."""
        questions = []
        
        if "fever" in [s.lower() for s in symptoms]:
            questions.append("How high is your fever and when did it start?")
            questions.append("Have you taken any medication for the fever?")
        
        if "headache" in [s.lower() for s in symptoms]:
            questions.append("Where exactly is the headache located?")
            questions.append("How would you describe the pain (sharp, dull, throbbing)?")
        
        if "cough" in [s.lower() for s in symptoms]:
            questions.append("Is the cough dry or do you produce phlegm?")
            questions.append("How long have you had the cough?")
        
        if not questions:
            questions.append("How long have you been experiencing these symptoms?")
            questions.append("Have you noticed any other changes in your health?")
        
        return questions[:3]  # Limit to 3 questions

    def _determine_urgency(self, patient_input: str, symptoms: List[str]) -> str:
        """Determine urgency level based on symptoms."""
        emergency_keywords = ["chest pain", "difficulty breathing", "severe bleeding", "loss of consciousness"]
        text_lower = patient_input.lower()
        
        for keyword in emergency_keywords:
            if keyword in text_lower:
                return "URGENT_MEDICAL_ATTENTION"
        
        # Check for severe symptoms
        severe_symptoms = ["high fever", "severe pain", "vomiting blood"]
        for symptom in severe_symptoms:
            if symptom in text_lower:
                return "PROMPT_MEDICAL_REVIEW"
        
        return "ROUTINE_CONSULTATION"

    def _mock_possible_conditions(self, symptoms: List[str]) -> List[Dict]:
        """Generate mock possible conditions based on symptoms."""
        conditions = []
        
        if "fever" in [s.lower() for s in symptoms]:
            conditions.append({
                "name": "Viral infection",
                "likelihood": "medium",
                "description": "Common viral infections include flu and common cold"
            })
        
        if "headache" in [s.lower() for s in symptoms]:
            conditions.append({
                "name": "Tension headache",
                "likelihood": "medium",
                "description": "Most common type of headache, often caused by stress"
            })
        
        if "cough" in [s.lower() for s in symptoms]:
            conditions.append({
                "name": "Upper respiratory infection",
                "likelihood": "medium",
                "description": "Infection of the nose, throat, or sinuses"
            })
        
        return conditions

    def _check_warning_signs(self, patient_input: str, symptoms: List[str]) -> List[str]:
        """Check for emergency warning signs."""
        warning_signs = []
        emergency_indicators = [
            "chest pain", "shortness of breath", "difficulty breathing",
            "severe pain", "sudden weakness", "slurred speech",
            "loss of consciousness", "confusion"
        ]
        
        text_lower = patient_input.lower()
        for indicator in emergency_indicators:
            if indicator in text_lower:
                warning_signs.append(indicator.replace("_", " ").capitalize())
        
        return warning_signs

    def _generate_general_information(self, symptoms: List[str]) -> str:
        """Generate general medical information."""
        if not symptoms:
            return "Please provide more details about your symptoms for better assessment."
        
        symptom_list = ", ".join(symptoms)
        return f"Based on the symptoms you've described ({symptom_list}), this could be related to several conditions. It's important to monitor your symptoms and seek professional medical advice if they persist or worsen."

    def _generate_recommendation(self, urgency_level: str) -> str:
        """Generate appropriate recommendation based on urgency."""
        recommendations = {
            "INFORMATIONAL": "Monitor your symptoms and maintain good hydration. Consult a healthcare provider if symptoms persist.",
            "ROUTINE_CONSULTATION": "Schedule an appointment with your healthcare provider within the next few days for proper evaluation.",
            "PROMPT_MEDICAL_REVIEW": "Seek medical attention within 24 hours for proper evaluation and treatment.",
            "URGENT_MEDICAL_ATTENTION": "Seek immediate medical attention. Call emergency services or go to the nearest emergency room."
        }
        
        return recommendations.get(urgency_level, recommendations["ROUTINE_CONSULTATION"])