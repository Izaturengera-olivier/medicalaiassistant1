"""
Custom exceptions for the Clinical Decision Support system.
"""


class MedicalSafetyError(Exception):
    """
    Raised when a medical safety rule is violated.
    """
    pass


class AuthenticationError(Exception):
    """
    Raised when authentication fails.
    """
    pass


class AuthorizationError(Exception):
    """
    Raised when authorization fails.
    """
    pass


class ConsultationError(Exception):
    """
    Raised when consultation operations fail.
    """
    pass


class AIServiceError(Exception):
    """
    Raised when AI service operations fail.
    """
    pass


class RetrievalError(Exception):
    """
    Raised when medical knowledge retrieval fails.
    """
    pass


class MedicationSafetyError(Exception):
    """
    Raised when medication safety checks identify issues.
    """
    pass
