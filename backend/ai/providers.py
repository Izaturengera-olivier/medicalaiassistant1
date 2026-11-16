"""Pluggable LLM provider interface. Real providers use an OpenAI-compatible API."""

import json
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import requests

from core.exceptions import AIServiceError, AIResponseTruncatedError

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.openai.com/v1"

# A free-tier Groq key allows ~8000 tokens per minute and one detailed answer costs
# 6k-7k, so a 429 is what a second question in the same minute looks like rather
# than a rare outage. Groq's own hint for that case is ~39s, so the cap must sit
# above it: waiting one window and answering beats handing the patient a template.
# 45s still leaves gunicorn's 120s request timeout plenty of room.
RATE_LIMIT_MAX_WAIT = 45.0
RATE_LIMIT_DEFAULT_WAIT = 8.0

# Reasoning models (openai/gpt-oss-20b on Groq) spend much of the completion on
# hidden reasoning tokens before emitting any JSON. Under the provider default
# budget the content comes back empty and Groq rejects the call with
# 400 json_validate_failed, which silently degrades users to the mock template.
# The budget must cover hidden reasoning PLUS a deliberately long, sectioned
# plain-text reply PLUS the rest of the JSON object. Measured on the live Groq
# endpoint with the depth prompts (3 cases: patient EN, patient Kinyarwanda,
# clinician EN): completion_tokens 3339-3653 with finish_reason=stop, so the old
# 4096 cap left only ~12% headroom and would clip the first slightly longer
# answer. 8192 is accepted by the endpoint and doubles that margin; anything
# clipped now raises AIResponseTruncatedError instead of passing silently.
# Prompt side measured 2654-4058 tokens, i.e. ~6.1k-7.4k tokens per call against
# the ~8k tokens/minute free-tier quota: about one call per minute sustained.
DEFAULT_MAX_TOKENS = 8192


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
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_tokens = max_tokens

    def complete_structured(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        for attempt in (1, 2):
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
                        "max_tokens": self.max_tokens,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                break
            except requests.HTTPError as exc:
                wait = self._rate_limit_wait(exc) if attempt == 1 else None
                if wait is None:
                    # The status line says "400 Bad Request"; the provider puts the
                    # actual reason (unknown model, bad param, quota) in the body.
                    body = getattr(exc.response, "text", "") or ""
                    raise AIServiceError(f"LLM request failed: {exc} — {body[:500]}") from exc
                logger.warning("LLM rate limited, retrying once in %.0fs", wait)
                time.sleep(wait)
            except requests.RequestException as exc:
                raise AIServiceError(f"LLM request failed: {exc}") from exc

        try:
            payload = response.json()
            choice = payload["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
            usage = payload.get("usage") or {}
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise AIServiceError(f"Unexpected LLM response shape: {exc}") from exc

        logger.info(
            "LLM completion model=%s finish_reason=%s prompt_tokens=%s completion_tokens=%s max_tokens=%s",
            self.model,
            finish_reason,
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
            self.max_tokens,
        )

        # A reply clipped by the budget arrives as truncated (often unparseable)
        # JSON and would otherwise be reported as "did not return valid JSON" or,
        # one layer up, vanish into the mock fallback with no clue why.
        if finish_reason == "length":
            logger.error(
                "LLM reply hit the completion budget (finish_reason=length, "
                "completion_tokens=%s, max_tokens=%s); raise the provider budget or shorten the prompt.",
                usage.get("completion_tokens"),
                self.max_tokens,
            )
            raise AIResponseTruncatedError(
                "The model answer was cut off because it reached the completion "
                f"limit of {self.max_tokens} tokens "
                f"(completion_tokens={usage.get('completion_tokens')})."
            )
        if finish_reason not in (None, "stop"):
            logger.warning("LLM generation stopped early: finish_reason=%s", finish_reason)

        return self._parse_json(content)

    @staticmethod
    def _rate_limit_wait(exc: requests.HTTPError) -> Optional[float]:
        """Seconds to wait before one retry on a rate limit, or None if not retryable."""
        response = getattr(exc, "response", None)
        if response is None or response.status_code != 429:
            return None

        header = (getattr(response, "headers", None) or {}).get("Retry-After", "")
        try:
            wait = float(str(header).strip())
        except (TypeError, ValueError):
            match = re.search(r"try again in ([0-9]+(?:\.[0-9]+)?)s", response.text or "")
            wait = float(match.group(1)) if match else RATE_LIMIT_DEFAULT_WAIT
        return wait if 0 < wait <= RATE_LIMIT_MAX_WAIT else None

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
        "model": "openai/gpt-oss-20b",
    },
}


def get_llm_provider(
    name: str,
    *,
    api_key: str = "",
    model: str = "",
    base_url: str = "",
    max_tokens: int = DEFAULT_MAX_TOKENS,
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
        max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
    )
