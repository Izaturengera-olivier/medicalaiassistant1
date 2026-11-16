"""Answers must be genuinely detailed, plain-text-safe, and truncation-detectable.

All of these run without network: the provider is either the deterministic mock
or a fake ``requests.post``.
"""

import logging

import pytest
import requests

from core.exceptions import AIServiceError, AIResponseTruncatedError

from ai.providers import DEFAULT_MAX_TOKENS, OpenAICompatibleProvider
from ai.services import AIService
from ai.services.ai_service import CONVERSATION_SCHEMA, PROFESSIONAL_SCHEMA
from ai.services.prompts import get_chat_system_prompt, get_professional_system_prompt

EVIDENCE_SAMPLE = (
    "[1] World Health Organization — Fever Guidance\n"
    "URL: https://www.who.int/fever\n"
    "Content: Fever is a raised temperature; check for neck stiffness and confusion."
)


def test_patient_prompt_asks_for_depth_not_brevity():
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "NO MARKDOWN" in prompt
    assert "150-300 words" in prompt
    assert "What this could mean" in prompt
    assert "Why it happens" in prompt
    assert "What to watch for" in prompt
    # The three phrases that used to suppress depth are gone.
    assert "clear, concise paragraphs" not in prompt
    assert "Provide only the concise conclusion" not in prompt


def test_emergency_replies_lead_with_the_urgent_instruction():
    """Live replies put the emergency advice last on two of three red-flag cases."""
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "the FIRST line of `reply` is the urgent instruction" in prompt
    assert "Never open such a reply with an explanation" in prompt


def test_follow_up_turns_do_not_repeat_the_earlier_assessment():
    """Live: "Should I take antibiotics for it?" repeated the whole first answer."""
    prompt = get_chat_system_prompt(
        evidence_block=EVIDENCE_SAMPLE, language="en", is_followup=True
    )

    assert "FOLLOW-UP TURN" in prompt
    assert "Start `reply` with a direct answer" in prompt
    assert "not another full assessment" in prompt


def test_opening_turn_carries_no_follow_up_block():
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "FOLLOW-UP TURN" not in prompt


def test_kinyarwanda_prompt_fixes_the_section_labels():
    """Live: one Kinyarwanda reply carried the English "To help me understand better"."""
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="rw")

    assert '"What this could mean" = "Ibyo bishoboka"' in prompt
    assert '"To help me understand better" = "Kugira ngo menye neza"' in prompt


def test_patient_prompt_selects_sections_instead_of_firing_every_one():
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "ONLY the 2-4 sections that genuinely fit" in prompt
    assert "DELETE the least relevant section" in prompt
    assert "never a quota to pad toward" in prompt


def test_prompt_keeps_grounding_and_safety_rules_intact():
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "NEVER invent medications" in prompt
    assert "Base every medical statement on the reference material below" in prompt
    assert "never tell a patient to start, stop, or change a medicine" in prompt
    assert "Cite evidence inline by its number" in prompt


def test_prompt_forbids_narrating_where_the_answer_came_from():
    """Patients should get a direct answer, not "according to our trusted sources"."""
    for prompt in (
        get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en"),
        get_professional_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en"),
    ):
        assert "VOICE (mandatory)" in prompt
        assert "NEVER describe how you obtained your answer" in prompt
        assert "according to trusted sources" in prompt  # listed as a banned phrase
        assert "the marker and the links shown by the interface" in prompt


def test_reference_material_is_not_presented_to_the_patient_as_sources():
    """The grounding instruction must not leak into the answer's own vocabulary."""
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "Ground every medical statement in the TRUSTED EVIDENCE" not in prompt
    assert "what the evidence implies" not in prompt


def test_depth_rules_work_in_kinyarwanda_and_keep_the_language_rules():
    prompt = get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="rw")

    assert "writing in Kinyarwanda" in prompt
    assert "KINYARWANDA QUALITY" in prompt
    assert "NEVER repeat" in prompt
    assert "150-300 words" in prompt
    assert "NO MARKDOWN" in prompt
    # Depth must never pull English section labels into a Kinyarwanda answer.
    assert "Never leave an English label inside a Kinyarwanda reply" in prompt
    assert "Ibyo bishoboka" in prompt


def test_professional_prompt_asks_for_clinical_depth():
    prompt = get_professional_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "200-350 words" in prompt
    assert "NO MARKDOWN" in prompt
    assert "Differentials" in prompt
    assert "Workup" in prompt
    assert "general clinical knowledge" in prompt
    # The brevity instruction that flattened clinician answers is gone.
    assert "Be direct, highly intelligent, and concise" not in prompt


def test_professional_prompt_allows_dosing_discussion_but_no_prescription():
    prompt = get_professional_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="rw")

    assert "Dosing and interaction considerations" in prompt
    assert "never a prescription order" in prompt.lower()
    assert "writing in Kinyarwanda" in prompt


def test_reply_fields_are_plain_text_everywhere():
    """The frontend renders the reply as plain text and feeds it to text-to-speech."""
    prompts = (
        get_chat_system_prompt(evidence_block=EVIDENCE_SAMPLE),
        get_professional_system_prompt(evidence_block=EVIDENCE_SAMPLE),
    )
    for prompt in prompts:
        assert "read aloud by text-to-speech" in prompt
        assert 'hyphen bullets that start with "- "' in prompt
        assert "code fences" in prompt
        # Measured live: the clinician reply pasted other schema fields into itself.
        assert 'never write labels such as "Urgency level:' in prompt
        # Measured live: the clinician reply leaked literal "\n" text.
        assert "Never output a literal backslash followed by n" in prompt


def test_professional_prompt_polices_uncited_clinical_claims():
    prompt = get_professional_system_prompt(evidence_block=EVIDENCE_SAMPLE, language="en")

    assert "Citation discipline" in prompt
    assert 'written with the words "general clinical knowledge"' in prompt
    assert "Never title a section as evidence or guidelines unless" in prompt


def test_schema_reply_descriptions_match_the_new_expectation():
    assert "150-300 words" in CONVERSATION_SCHEMA["reply"]
    assert "200-350 words" in PROFESSIONAL_SCHEMA["reply"]
    for schema in (CONVERSATION_SCHEMA, PROFESSIONAL_SCHEMA):
        assert "NO markdown" in schema["reply"]
        assert "inline [1] citations" in schema["reply"]
    assert "short paragraphs or tight bullets" not in PROFESSIONAL_SCHEMA["reply"]
    assert "conversational reply to the patient" not in CONVERSATION_SCHEMA["reply"]


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error", response=self)


def _completion(content, finish_reason, usage=None):
    return {
        "choices": [{"message": {"content": content}, "finish_reason": finish_reason}],
        "usage": usage or {"prompt_tokens": 3020, "completion_tokens": 8192},
    }


def test_finish_reason_length_raises_a_distinct_truncation_error(monkeypatch):
    """A clipped long answer must be diagnosable, not a vague JSON parse failure."""
    monkeypatch.setattr(
        requests,
        "post",
        lambda *a, **kw: _FakeResponse(
            _completion('{"reply": "cut mid sentence', "length")
        ),
    )
    provider = OpenAICompatibleProvider(api_key="k", model="m", max_tokens=8192)

    with pytest.raises(AIResponseTruncatedError, match="completion limit of 8192"):
        provider.complete_structured([{"role": "user", "content": "fever"}], {})

    assert issubclass(AIResponseTruncatedError, AIServiceError)


def test_completion_budget_covers_a_measured_long_reply():
    """Live Groq runs produced 3339-3653 completion tokens with finish_reason=stop,
    so the budget has to sit clearly above that or depth silently truncates."""
    assert DEFAULT_MAX_TOKENS >= 8192


def test_normal_stop_is_not_treated_as_truncation(monkeypatch):
    monkeypatch.setattr(
        requests,
        "post",
        lambda *a, **kw: _FakeResponse(
            _completion('{"reply": "fine", "urgency_level": "INFORMATIONAL"}', "stop"),
        ),
    )
    provider = OpenAICompatibleProvider(api_key="k", model="m")
    assert provider.complete_structured([], {})["reply"] == "fine"


class _TruncatingProvider:
    def __init__(self):
        self.calls = 0

    def complete_structured(self, messages, schema):
        self.calls += 1
        raise AIResponseTruncatedError(
            "The model answer was cut off because it reached the completion limit of 8192 tokens."
        )


@pytest.fixture
def truncating(settings, monkeypatch):
    settings.AI_PROVIDER = "openai"
    settings.AI_API_KEY = "test-key"
    provider = _TruncatingProvider()
    monkeypatch.setattr(
        "ai.services.ai_service.get_llm_provider", lambda *args, **kwargs: provider
    )
    return provider


@pytest.mark.django_db
def test_truncation_is_logged_as_an_error_not_a_plain_fallback(truncating, caplog):
    with caplog.at_level(logging.WARNING):
        AIService().converse("I have had a headache for three days and my neck feels stiff")

    assert truncating.calls == 1
    errors = [
        record
        for record in caplog.records
        if record.levelno >= logging.ERROR and "truncat" in record.getMessage().lower()
    ]
    assert errors, "a truncated reply must be logged loudly"


@pytest.mark.django_db
def test_professional_fallback_names_the_real_cause(truncating):
    result = AIService().converse_professional(
        "65F, epigastric pain 3 weeks, weight loss - differential and workup?"
    )

    text = result["reply"].lower()
    assert "the model answer could not be used" in text
    assert "no llm provider is configured" not in text
    assert result["model_used"] == "mock"


@pytest.mark.django_db
def test_missing_provider_still_reports_missing_provider():
    """The honest 'no key configured' note must survive for the real unconfigured case."""
    from django.conf import settings as django_settings

    django_settings.AI_PROVIDER = "mock"
    django_settings.AI_API_KEY = ""
    result = AIService().converse_professional("Interaction risk of metronidazole with warfarin?")

    assert "no llm provider is configured" in result["reply"].lower()


@pytest.mark.django_db
def test_converse_asks_retrieval_for_the_widened_evidence_window(monkeypatch):
    service = AIService()
    seen = {}
    original = service.retrieval_service.retrieve_evidence

    def spy(query, max_results=4, **kwargs):
        seen["max_results"] = max_results
        return original(query=query, max_results=max_results, **kwargs)

    monkeypatch.setattr(service.retrieval_service, "retrieve_evidence", spy)
    service.converse("I have fever and headache")

    assert seen["max_results"] == AIService.MAX_EVIDENCE_RESULTS
    assert AIService.MAX_EVIDENCE_RESULTS >= 8


def test_double_escaped_newlines_become_real_line_breaks():
    """Measured live: the model sometimes emits a literal backslash-n inside the
    JSON string, which pre-wrap would render as visible "\n" text."""
    service = AIService()
    raw = {
        "reply": "Differentials\\n- Peptic ulcer\\n- GERD",
        "urgency_level": "PROMPT_MEDICAL_REVIEW",
    }
    result = service._normalize_result(raw, [])

    assert "\\n" not in result["reply"]
    assert result["reply"].splitlines() == ["Differentials", "- Peptic ulcer", "- GERD"]


def test_normal_newlines_are_left_alone():
    service = AIService()
    result = service._normalize_result(
        {"reply": "What this could mean\n- Meningitis", "urgency_level": "INFORMATIONAL"}, []
    )

    assert "\n- Meningitis" in result["reply"]


def _evidence():
    return [
        {
            "title": "Fever Guidance",
            "source_name": "World Health Organization",
            "url": "https://www.who.int/fever",
            "content": "Fever is a raised temperature; check for neck stiffness.",
        },
        {
            "title": "Meningitis",
            "source_name": "World Health Organization",
            "url": "https://www.who.int/meningitis",
            "content": "Neck stiffness with confusion needs urgent care.",
        },
    ]


def test_offline_fallback_reply_does_not_narrate_sources():
    reply = AIService()._mock_conversation(
        "I have a fever and a stiff neck",
        [{"role": "user", "content": "I have a fever and a stiff neck"}],
        None,
        None,
        _evidence(),
    )["reply"]

    for banned in ("trusted sources", "approved medical sources", "nkomoko", "i searched"):
        assert banned not in reply.lower()
    assert "[1]" in reply


def test_offline_fallback_skips_passages_that_only_share_a_word():
    """The reported case: "ni ibihe bitaro bikomeye mu rwanda" retrieved the Malaria
    page at relevance 1 and the fallback presented it as an answer."""
    noise = [{
        "title": "Malaria Signs and When to Seek Care",
        "source_name": "World Health Organization",
        "url": "https://www.who.int/malaria",
        "content": "Malaria is common in Rwanda.",
        "relevance_score": 1.0,
    }]
    service = AIService()

    reply = service._mock_conversation(
        "ni ibihe bitaro bikomeye mu rwanda",
        [{"role": "user", "content": "ni ibihe bitaro bikomeye mu rwanda"}],
        None,
        None,
        noise,
    )["reply"]
    professional = service._mock_professional_conversation(
        "which are the major hospitals in rwanda", [], noise
    )["reply"]

    assert "Malaria" not in reply
    assert "Amakuru y'ubuzima bijyanye" not in reply
    assert "Ntabwo mfite amakuru ahagije" in reply
    assert "Malaria" not in professional
    assert "Ingingo zifitanye isano" not in professional


def test_fallback_keeps_marker_positions_of_the_passages_it_presents():
    service = AIService()
    evidence = [
        {
            "title": "Noise",
            "source_name": "WHO",
            "url": "https://www.who.int/noise",
            "content": "unrelated",
            "relevance_score": 1.0,
        },
        {
            "title": "Fever Guidance",
            "source_name": "WHO",
            "url": "https://www.who.int/fever",
            "content": "Fever is a raised temperature.",
            "relevance_score": 3.0,
        },
    ]

    reply = service._mock_conversation("fever", [], None, None, evidence)["reply"]

    assert "[2] Fever Guidance" in reply
    assert "[1] Noise" not in reply
    assert service._evidence_sources(evidence)[1]["url"] == "https://www.who.int/fever"


def test_provider_failure_does_not_dress_up_unrelated_passages_as_an_answer():
    """A rate-limited minute used to produce template text plus loosely-matched
    passages, which the patient reported as an irrelevant clinical answer."""
    service = AIService()

    result = service._mock_conversation(
        "I have had a headache for three days",
        [{"role": "user", "content": "I have had a headache for three days"}],
        None,
        None,
        _evidence(),
        fallback_reason="429 Too Many Requests",
    )

    assert result["model_used"] == "mock"
    assert "briefly busy" in result["reply"]
    assert "Health information relevant to what you described" not in result["reply"]
    assert "[" not in result["reply"]  # no citation to content it did not answer from
    assert result["sources"] == []


def test_citation_markers_map_onto_the_sources_array():
    """[n] in the reply must resolve to sources[n-1] so the UI can link it."""
    sources = AIService()._evidence_sources(_evidence())

    assert [item["index"] for item in sources] == [1, 2]
    assert sources[0]["url"] == "https://www.who.int/fever"
    assert sources[1]["name"] == "World Health Organization"


def test_duplicate_urls_keep_their_own_numbers():
    evidence = _evidence() + [_evidence()[0]]

    sources = AIService()._evidence_sources(evidence)

    assert [item["index"] for item in sources] == [1, 2, 3]
    assert sources[2]["url"] == sources[0]["url"]
