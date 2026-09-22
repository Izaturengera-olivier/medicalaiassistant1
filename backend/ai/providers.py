"""Pluggable LLM provider interface. Real providers are wired in Phase 6."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def complete_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Deterministic stub so later phases can develop without an API key."""

    def complete_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "symptoms_identified": [],
            "follow_up_questions": [
                "How long have you had these symptoms?",
            ],
            "possible_conditions": [],
            "warning_signs": [],
            "urgency_level": "INFORMATIONAL",
            "general_information": (
                "This is a mock response used until an LLM provider is configured. "
                "It is not medical advice and is not a diagnosis."
            ),
            "medication_information": [],
            "recommended_next_step": "Consult a qualified healthcare professional.",
            "sources": [],
        }


def get_llm_provider(name: str) -> LLMProvider:
    if name == "mock":
        return MockLLMProvider()
    raise NotImplementedError(f"LLM provider {name!r} is not configured yet.")
