"""
Custom validators for the Clinical Decision Support system.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_medical_text(value):
    """
    Validate that text does not contain malicious content or unsupported medical claims.
    """
    # Basic validation - will be expanded in later phases
    if not value or not value.strip():
        raise ValidationError(_("This field cannot be empty."))
    
    # Additional validation will be added in Phase 6 for AI safety
    return value


def validate_date_of_birth(value):
    """
    Validate date of birth is reasonable.
    """
    from datetime import date
    import datetime
    
    if not value:
        raise ValidationError(_("Date of birth is required."))
    
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    
    if age < 0 or age > 150:
        raise ValidationError(_("Invalid date of birth."))
    
    return value


def validate_medication_dosage(value):
    """
    Validate medication dosage format.
    """
    # Basic validation - will be expanded in Phase 10
    if not value or not value.strip():
        raise ValidationError(_("Dosage cannot be empty."))
    return value
