"""Tests for the pluggable LLM provider layer."""

import pytest
import requests

from core.exceptions import AIServiceError

from ai.providers import (
    DEFAULT_BASE_URL,
    MockLLMProvider,
    OpenAICompatibleProvider,
    get_llm_provider,
)


class _FakeResponse:
    def __init__(self, payload, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text

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
