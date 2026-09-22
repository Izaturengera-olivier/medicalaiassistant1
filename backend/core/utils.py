"""
Utility functions for the Clinical Decision Support system.
"""

from datetime import datetime, timedelta
from typing import Optional


def calculate_age(birth_date: datetime) -> int:
    """
    Calculate age from birth date.
    """
    today = datetime.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def format_date(date: datetime, format: str = "%Y-%m-%d") -> str:
    """
    Format date to string.
    """
    if date is None:
        return ""
    return date.strftime(format)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length with ellipsis.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def sanitize_medical_text(text: str) -> str:
    """
    Sanitize medical text for safe display.
    """
    # Basic sanitization - will be expanded in later phases
    return text.strip()


def generate_unique_id() -> str:
    """
    Generate a unique identifier for consultations or records.
    """
    import uuid
    return str(uuid.uuid4())


def is_emergency_symptom(symptoms: list) -> bool:
    """
    Check if symptoms indicate emergency.
    """
    # Basic implementation - will be expanded in Phase 6
    emergency_keywords = ['chest pain', 'difficulty breathing', 'severe bleeding', 'loss of consciousness']
    symptoms_lower = [s.lower() for s in symptoms]
    return any(keyword in ' '.join(symptoms_lower) for keyword in emergency_keywords)
