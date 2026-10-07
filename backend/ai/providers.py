"""Pluggable LLM provider interface. Real providers use an OpenAI-compatible API."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import requests

from core.exceptions import AIServiceError

DEFAULT_BASE_URL = "https://api.openai.com/v1"


class LLMProvider(ABC):
    """Chat-completion provider that returns a structured JSON response."""

    @abstractmethod
    def complete_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Complete a chat conversation and return the reply parsed as JSON."""
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Deterministic stub so the app runs without an API key."""

    def complete_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "reply": (
                "This is a mock response used until an LLM provider is configured. "
                "It is not medical advice and is not a diagnosis."
            ),
            "symptoms_identified": [],
            "follow_up_questions": ["How long have you had these symptoms?"],
            "possible_conditions": [],
            "warning_signs": [],
            "urgency_level": "INFORMATIONAL",
            "general_information": "",
            "medication_information": [],
            "recommended_next_step": "Consult a qualified healthcare professional.",
            "sources": [],
        }


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI-compatible chat completions (OpenAI, Groq, Ollama, vLLM, ...)."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": self._with_schema(messages, schema),
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            # The status line says "400 Bad Request"; the provider puts the actual
            # reason (unknown model, bad param, quota) in the response body.
            body = getattr(exc.response, "text", "") or ""
            raise AIServiceError(f"LLM request failed: {exc} — {body[:500]}") from exc
        except requests.RequestException as exc:
            raise AIServiceError(f"LLM request failed: {exc}") from exc

        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise AIServiceError(f"Unexpected LLM response shape: {exc}") from exc

        return self._parse_json(content)

    @staticmethod
    def _with_schema(
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        instruction = (
            "Respond with a single JSON object matching this schema:\n"
            + json.dumps(schema, ensure_ascii=False)
        )
        if messages and messages[0].get("role") == "system":
            return [
                {**messages[0], "content": f"{messages[0]['content']}\n\n{instruction}"},
                *messages[1:],
            ]
        return [{"role": "system", "content": instruction}, *messages]

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        text = (content or "").strip()
        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start == -1 or end <= start:
                raise AIServiceError("LLM did not return valid JSON.")
            try:
                data = json.loads(text[start : end + 1])
            except json.JSONDecodeError as exc:
                raise AIServiceError(f"LLM did not return valid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise AIServiceError("LLM JSON response is not an object.")
        return data


PROVIDER_DEFAULTS = {
    "openai": {
        "base_url": DEFAULT_BASE_URL,
        "model": "gpt-4o-mini",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
    },
}


def get_llm_provider(
    name: str,
    *,
    api_key: str = "",
    model: str = "",
    base_url: str = "",
) -> LLMProvider:
    if name == "mock":
        return MockLLMProvider()
    if not api_key:
        raise AIServiceError(f"AI provider {name!r} requires AI_API_KEY to be configured.")

    defaults = PROVIDER_DEFAULTS.get(name.lower(), {})
    resolved_base_url = base_url or defaults.get("base_url") or DEFAULT_BASE_URL
    resolved_model = model or defaults.get("model") or "gpt-4o-mini"

    return OpenAICompatibleProvider(
        api_key=api_key,
        model=resolved_model,
        base_url=resolved_base_url,
    )
