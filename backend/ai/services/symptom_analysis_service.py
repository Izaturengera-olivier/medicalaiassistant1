"""Service for analyzing and extracting symptoms from patient input."""

import re
from typing import List, Dict, Any
from django.utils.translation import gettext_lazy as _


class SymptomAnalysisService:
    """Service for analyzing patient symptoms from natural language input in English and Kinyarwanda."""

    # Common symptom patterns and keywords (English and Kinyarwanda)
    SYMPTOM_PATTERNS = {
        "headache": [
            "headache", "head pain", "migraine", "cephalgia",
            "umutwe", "umutwe urampandura", "umutwe urandya", "kuribwa mu mutwe"
        ],
        "fever": [
            "fever", "high temperature", "pyrexia", "hot", "temperature",
            "umuriro", "ubushyuhe", "gushyuha", "furere", "gutitira"
        ],
        "cough": [
            "cough", "coughing", "chesty cough", "dry cough",
            "inkorora", "gukosora", "kosora"
        ],
        "body pain": [
            "body pain", "body ache", "muscle pain", "myalgia", "soreness",
            "ububabare mu mubiri", "umubiri urambabaza", "kuribwa mu mubiri", "ngingo"
        ],
        "stomach pain": [
            "stomach pain", "abdominal pain", "belly pain", "gastralgia",
            "nda", "mu nda", "ububabare mu nda", "ndababara mu nda", "mbabara mu nda",
            "igifu", "igifu kirandya", "ububabare bwo mu igifu"
        ],
        "nausea": [
            "nausea", "feeling sick", "queasy", "upset stomach",
            "gusesema", "isesemi", "isazi", "igifu kigurumana"
        ],
        "vomiting": [
            "vomiting", "throwing up", "emesis", "throw up",
            "kuruka", "kuhira", "vomissman"
        ],
        "diarrhea": [
            "diarrhea", "diarrhoea", "loose stools", "frequent bowel movements",
            "impiswi", "gucibwamo", "gutuza"
        ],
        "fatigue": [
            "fatigue", "tiredness", "exhaustion", "weakness", "lethargy",
            "umunaniro", "naniwe", "kuruha", "gucika intege"
        ],
        "dizziness": [
            "dizziness", "lightheaded", "vertigo", "spinning",
            "kuzungerwa", "ikizunguzungu", "ibingibingi"
        ],
        "chest pain": [
            "chest pain", "chest discomfort", "chest pressure", "angina",
            "mu gituza", "mu gatuza", "ububabare mu gituza", "igituza kirambabaza", "gituza", "gatuza"
        ],
        "shortness of breath": [
            "shortness of breath", "breathlessness", "dyspnea", "difficulty breathing",
            "guhumeka bigoranye", "kubura umwuka", "umwuka wanjye", "uhumeka nabi"
        ],
        "sore throat": [
            "sore throat", "throat pain", "pharyngitis", "scratchy throat",
            "muhogo", "ububabare mu muhogo", "umuhogo urambabaza"
        ],
        "runny nose": [
            "runny nose", "rhinorrhea", "stuffy nose", "nasal congestion",
            "ibicurane", "amazuru itemba", "gutana mu mazuru"
        ],
        "sneezing": [
            "sneezing", "sneeze", "kwasamura"
        ],
        "rash": [
            "rash", "skin rash", "hives", "itchy skin",
            "ibiheri", "uburuka", "uruhu rurandya", "ku ryaryata"
        ],
        "swelling": [
            "swelling", "edema", "inflammation", "puffiness",
            "kubyimba", "kubyimbya"
        ],
        "back pain": [
            "back pain", "lower back pain", "lumbar pain",
            "umugongo", "ububabare mu mugongo", "mbabara umugongo", "umugongo urambabaza"
        ]
    }

    # Duration patterns (English and Kinyarwanda)
    DURATION_PATTERNS = [
        r"(\d+)\s*(day|days|d|iminsi|umunsi)",
        r"(\d+)\s*(week|weeks|w|ibyumweru|icyumweru)",
        r"(\d+)\s*(month|months|m|amezi|ukwezi)",
        r"(\d+)\s*(hour|hours|h|amasaha|isaha)",
        r"(\d+)\s*(minute|minutes|min|iminota)",
        r"(today|yesterday|ejo|ejo hashize|uyu munsi)",
        r"(a few days|several days|couple of days|iminsi mike|iminsi 2|iminsi 3)",
    ]

    # Severity indicators (English and Kinyarwanda)
    SEVERITY_INDICATORS = {
        "mild": ["mild", "slight", "minor", "low", "light", "byoroheje", "gake", "bikerense"],
        "moderate": ["moderate", "medium", "some", "fair", "biringaniye", "biragabanyutse"],
        "severe": ["severe", "bad", "terrible", "awful", "extreme", "intense", "strong", "cyane", "gikabije", "bikarishye"],
    }

    @classmethod
    def extract_symptoms(cls, text: str) -> List[str]:
        """
        Extract symptoms from natural language text in English or Kinyarwanda.
        
        Args:
            text: Patient's description of symptoms
            
        Returns:
            List of identified symptoms
        """
        text_lower = text.lower()
        identified_symptoms = []
        
        for symptom, patterns in cls.SYMPTOM_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    if symptom not in identified_symptoms:
                        identified_symptoms.append(symptom)
                    break
        
        return identified_symptoms

    @classmethod
    def extract_duration(cls, text: str) -> str:
        """
        Extract duration information from text.
        
        Args:
            text: Patient's description
            
        Returns:
            Duration string or empty string if not found
        """
        for pattern in cls.DURATION_PATTERNS:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(0)
        
        return ""

    @classmethod
    def determine_severity(cls, text: str) -> str:
        """
        Determine symptom severity from text.
        
        Args:
            text: Patient's description
            
        Returns:
            Severity level (mild, moderate, severe)
        """
        text_lower = text.lower()
        
        for severity, indicators in cls.SEVERITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return severity
        
        return "moderate"  # Default severity

    @classmethod
    def analyze_symptom_description(cls, text: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of symptom description.
        
        Args:
            text: Patient's symptom description
            
        Returns:
            Dictionary with extracted information
        """
        return {
            "symptoms": cls.extract_symptoms(text),
            "duration": cls.extract_duration(text),
            "severity": cls.determine_severity(text),
            "raw_text": text,
            "word_count": len(text.split()),
            "has_emergency_keywords": cls._check_emergency_keywords(text)
        }

    @classmethod
    def _check_emergency_keywords(cls, text: str) -> bool:
        """Check for emergency warning signs in English and Kinyarwanda."""
        emergency_keywords = [
            "chest pain", "difficulty breathing", "shortness of breath",
            "severe bleeding", "loss of consciousness", "confusion",
            "slurred speech", "sudden weakness", "stroke", "heart attack",
            "ububabare mu gituza", "ububabare mu gatuza", "ndababara mu gatuza", "kubura umwuka", "kuva amaraso cyane",
            "guta ubwenge", "gucika intege ku ruhande", "kuruka amaraso"
        ]
        
        text_lower = text.lower()
        for keyword in emergency_keywords:
            if keyword in text_lower:
                return True
        
        return False

    @classmethod
    def get_missing_information(cls, analysis: Dict[str, Any]) -> List[str]:
        """
        Identify what information is missing from the analysis.
        
        Args:
            analysis: Result from analyze_symptom_description
            
        Returns:
            List of missing information types
        """
        missing = []
        
        if not analysis["symptoms"]:
            missing.append("specific symptoms")
        if not analysis["duration"]:
            missing.append("duration of symptoms")
        if analysis["word_count"] < 5:
            missing.append("more detailed description")
        
        return missing