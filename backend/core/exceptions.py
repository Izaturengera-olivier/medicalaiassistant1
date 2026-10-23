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


class AIResponseTruncatedError(AIServiceError):
    """
    Raised when the provider stopped generating because the completion budget ran
    out. Distinct from a generic failure so a clipped answer is diagnosable
    instead of silently degrading into the mock fallback template.
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


class DocumentParseError(Exception):
    """
    Raised when an uploaded file is rejected or cannot be turned into readable text.
    """
    pass
