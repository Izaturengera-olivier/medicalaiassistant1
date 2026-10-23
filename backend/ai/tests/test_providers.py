"""Tests for the pluggable LLM provider layer."""

import pytest
import requests

from core.exceptions import AIServiceError

from ai.providers import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    MockLLMProvider,
    OpenAICompatibleProvider,
    get_llm_provider,
)


class _FakeResponse:
    def __init__(self, payload, status_code=200, text="", headers=None):
        self._payload = payload
        self.status_code = status_code
        self.text = text
        self.headers = headers or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            # Real requests attaches the response to the error; callers rely on it.
            raise requests.HTTPError(f"{self.status_code} error", response=self)


def test_factory_returns_mock_provider():
    assert isinstance(get_llm_provider("mock"), MockLLMProvider)


def test_factory_without_api_key_raises():
    with pytest.raises(AIServiceError):
        get_llm_provider("openai", api_key="")


def test_factory_builds_openai_compatible_provider():
    provider = get_llm_provider("groq", api_key="k", model="llama-3.1-8b", base_url="https://api.groq.com/openai/v1/")
    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.base_url == "https://api.groq.com/openai/v1"
    assert provider.model == "llama-3.1-8b"


def test_factory_defaults_base_url():
    provider = get_llm_provider("openai", api_key="k")
    assert provider.base_url == DEFAULT_BASE_URL
    assert provider.model == "gpt-4o-mini"


def test_factory_resolves_deepseek_preset():
    provider = get_llm_provider("deepseek", api_key="k")
    assert provider.base_url == "https://api.deepseek.com"
    assert provider.model == "deepseek-chat"


def test_factory_resolves_gemini_preset():
    provider = get_llm_provider("gemini", api_key="k")
    assert provider.base_url == "https://generativelanguage.googleapis.com/v1beta/openai"
    assert provider.model == "gemini-2.5-flash"


def test_mock_provider_returns_conversational_reply():
    result = MockLLMProvider().complete_structured([{"role": "user", "content": "hi"}], {})
    assert result["reply"]
    assert isinstance(result["follow_up_questions"], list)


def test_complete_structured_parses_json(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["body"] = json
        return _FakeResponse({
            "choices": [{"message": {"content": '{"reply": "hello", "urgency_level": "ROUTINE_CONSULTATION"}'}}]
        })

    monkeypatch.setattr(requests, "post", fake_post)

    provider = OpenAICompatibleProvider(api_key="secret", model="gpt-4o-mini")
    result = provider.complete_structured(
        [{"role": "system", "content": "be safe"}, {"role": "user", "content": "fever"}],
        {"reply": "string"},
    )

    assert result == {"reply": "hello", "urgency_level": "ROUTINE_CONSULTATION"}
    assert captured["url"] == f"{DEFAULT_BASE_URL}/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer secret"
    assert captured["body"]["model"] == "gpt-4o-mini"
    # Reasoning models spend the completion budget on hidden tokens first; without
    # an explicit budget Groq returns empty content and a 400 json_validate_failed.
    assert captured["body"]["max_tokens"] == DEFAULT_MAX_TOKENS
    # The schema instruction is appended to the existing system message.
    assert "matching this schema" in captured["body"]["messages"][0]["content"]
    assert captured["body"]["messages"][1] == {"role": "user", "content": "fever"}


def test_complete_structured_parses_fenced_json(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *a, **kw: _FakeResponse({
            "choices": [{"message": {"content": "```json\n{\"reply\": \"ok\"}\n```"}}]
        }),
    )
    provider = OpenAICompatibleProvider(api_key="k", model="m")
    assert provider.complete_structured([], {})["reply"] == "ok"


def test_complete_structured_raises_on_http_error(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _FakeResponse({}, status_code=401))
    provider = OpenAICompatibleProvider(api_key="bad", model="m")
    with pytest.raises(AIServiceError):
        provider.complete_structured([], {})


def test_http_error_message_includes_provider_body(monkeypatch):
    """A bare status line is useless for debugging; surface the provider's reason."""
    monkeypatch.setattr(
        requests,
        "post",
        lambda *a, **kw: _FakeResponse(
            {}, status_code=400, text='{"error":"The model `x` does not exist"}'
        ),
    )
    provider = OpenAICompatibleProvider(api_key="k", model="x")

    with pytest.raises(AIServiceError, match="does not exist"):
        provider.complete_structured([], {})


def test_complete_structured_raises_on_non_json_content(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *a, **kw: _FakeResponse({"choices": [{"message": {"content": "not json at all"}}]}),
    )
    provider = OpenAICompatibleProvider(api_key="k", model="m")
    with pytest.raises(AIServiceError):
        provider.complete_structured([], {})


def test_complete_structured_raises_on_unexpected_shape(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _FakeResponse({"choices": []}))
    provider = OpenAICompatibleProvider(api_key="k", model="m")
    with pytest.raises(AIServiceError):
        provider.complete_structured([], {})


def _ok_response():
    return _FakeResponse({
        "choices": [
            {"message": {"content": '{"reply": "detailed answer"}'}, "finish_reason": "stop"}
        ]
    })


def _patch_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr(
        "ai.providers.time.sleep", lambda seconds: slept.append(seconds)
    )
    return slept


def test_rate_limit_retry_recovers_from_a_short_window(monkeypatch):
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _FakeResponse({}, status_code=429, headers={"Retry-After": "3"})
        return _ok_response()

    monkeypatch.setattr(requests, "post", fake_post)
    slept = _patch_sleep(monkeypatch)

    provider = OpenAICompatibleProvider(api_key="k", model="m")
    result = provider.complete_structured([], {})

    assert result["reply"] == "detailed answer"
    assert calls["n"] == 2
    assert slept == [3.0]


def test_rate_limit_falls_back_immediately_when_the_window_is_too_long(monkeypatch):
    """A two-minute wait must not stall the chat; the fallback answers instead."""
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        return _FakeResponse({}, status_code=429, headers={"Retry-After": "120"})

    monkeypatch.setattr(requests, "post", fake_post)
    slept = _patch_sleep(monkeypatch)

    provider = OpenAICompatibleProvider(api_key="k", model="m")
    with pytest.raises(AIServiceError, match="429"):
        provider.complete_structured([], {})

    assert calls["n"] == 1
    assert slept == []


def test_rate_limit_reads_the_groq_retry_hint_from_the_body(monkeypatch):
    """Groq names the wait in its message, not always in a Retry-After header."""
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _FakeResponse(
                {},
                status_code=429,
                text="Rate limit reached for model on tokens per minute (TPM): "
                     "Limit 8000, Used 4672, Requested 6248. Please try again in 21.9s.",
            )
        return _ok_response()

    monkeypatch.setattr(requests, "post", fake_post)
    slept = _patch_sleep(monkeypatch)

    provider = OpenAICompatibleProvider(api_key="k", model="m")
    assert provider.complete_structured([], {})["reply"] == "detailed answer"

    assert slept == [21.9]


def test_a_second_rate_limit_is_not_retried_again(monkeypatch):
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        return _FakeResponse({}, status_code=429, headers={"Retry-After": "1"})

    monkeypatch.setattr(requests, "post", fake_post)
    slept = _patch_sleep(monkeypatch)

    provider = OpenAICompatibleProvider(api_key="k", model="m")
    with pytest.raises(AIServiceError, match="429"):
        provider.complete_structured([], {})

    assert calls["n"] == 2
    assert slept == [1.0]
