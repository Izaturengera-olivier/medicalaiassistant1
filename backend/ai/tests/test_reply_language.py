"""The LLM must be told to answer in the language the user wrote in."""

import pytest

from ai.services import AIService, SymptomAnalysisService


class RecordingProvider:
    """Stands in for a real LLM so tests never hit the network."""

    def __init__(self):
        self.messages = None

    def complete_structured(self, messages, schema):
        self.messages = messages
        return {"reply": "ok", "urgency_level": "INFORMATIONAL"}


@pytest.fixture
def provider(settings, monkeypatch):
    settings.AI_PROVIDER = "openai"
    settings.AI_API_KEY = "test-key"
    recording = RecordingProvider()
    monkeypatch.setattr(
        "ai.services.ai_service.get_llm_provider", lambda *args, **kwargs: recording
    )
    return recording


def system_prompt_of(provider):
    return provider.messages[0]["content"]


@pytest.mark.django_db
class TestPatientReplyLanguage:
    def test_kinyarwanda_message_requests_kinyarwanda_reply(self, provider):
        AIService().converse("mfite umuriro n'inkorora kuva ejo")
        assert "writing in Kinyarwanda" in system_prompt_of(provider)

    def test_english_message_requests_english_reply(self, provider):
        AIService().converse("I have had a fever and a cough for two days")
        prompt = system_prompt_of(provider)
        assert "writing in English" in prompt
        assert "writing in Kinyarwanda" not in prompt

    def test_kinyarwanda_detection_with_grammatical_prefix(self, provider):
        AIService().converse("Ndababara mu nda kuva amasaha abiri")
        assert "writing in Kinyarwanda" in system_prompt_of(provider)

    def test_english_message_with_a_kinyarwanda_symptom_word_replies_in_english(self, provider):
        """Measured live: a mostly-English question returned a Kinyarwanda answer."""
        AIService().converse("I have umuriro and headache, can I take paracetamol?")

        prompt = system_prompt_of(provider)
        assert "writing in English" in prompt
        assert "writing in Kinyarwanda" not in prompt

    def test_follow_up_conversation_gets_follow_up_instructions(self, provider):
        """Live: a short follow-up repeated the whole opening assessment."""
        history = [
            {"role": "user", "content": "I have a runny nose and sneeze every morning."},
            {"role": "assistant", "content": "This looks like allergic rhinitis."},
        ]
        AIService().converse("Should I take antibiotics for it?", history=history)

        assert "FOLLOW-UP TURN" in system_prompt_of(provider)

    def test_kinyarwanda_question_nakoresha_iki_detected_as_kinyarwanda(self, provider):
        AIService().converse("nakoresha iki ngo bigabanuke?")
        assert "writing in Kinyarwanda" in system_prompt_of(provider)

    def test_kinyarwanda_question_in_mock_fallback(self):
        res = AIService().converse("nakoresha iki ngo bigabanuke?")
        reply_lower = res["reply"].lower()
        assert "murakoze" in reply_lower or "kugira ngo" in reply_lower or "amakuru" in reply_lower or "kugabanya" in reply_lower
        assert "thanks — i've noted" not in reply_lower


@pytest.mark.django_db
class TestProfessionalReplyLanguage:
    def test_kinyarwanda_case_requests_kinyarwanda_reply(self, provider):
        AIService().converse_professional("mfite umurwayi ufite umuriro n'inkorora")
        assert "writing in Kinyarwanda" in system_prompt_of(provider)

    def test_english_case_requests_english_reply(self, provider):
        AIService().converse_professional(
            "Interaction risk of metronidazole with warfarin?"
        )
        prompt = system_prompt_of(provider)
        assert "writing in English" in prompt
        assert "writing in Kinyarwanda" not in prompt


@pytest.mark.django_db
class TestFrenchReplyLanguage:
    def test_french_message_requests_french_reply(self, provider):
        AIService().converse("J'ai de la fièvre et une toux depuis deux jours")
        prompt = system_prompt_of(provider)

        assert "writing in French" in prompt
        assert "writing in Kinyarwanda" not in prompt
        assert "writing in English" not in prompt

    def test_french_health_question_stays_french(self, provider):
        AIService().converse("J'ai mal à la tête depuis deux jours, que faire ?")

        assert "writing in French" in system_prompt_of(provider)

    def test_kinyarwanda_with_one_french_looking_word_stays_kinyarwanda(self, provider):
        AIService().converse("Mfite umuriro n'inkorora, nkore iki?")

        assert "writing in Kinyarwanda" in system_prompt_of(provider)

    def test_a_lowercase_rwandan_place_name_keeps_an_english_question_english(self):
        """Live: "where rwankeri health center located?" was answered in Kinyarwanda."""
        message = "where rwankeri health center located? i want sector"

        assert AIService()._detect_language(message, []) == "en"


@pytest.mark.django_db
class TestAnswerTheExactQuestion:
    def test_patient_prompt_forbids_substituting_a_nearby_list(self, provider):
        AIService().converse("I have had a fever for two days, what should I do?")
        prompt = system_prompt_of(provider)

        assert "ANSWER THE EXACT QUESTION" in prompt
        assert "latest message wins" in prompt

    def test_professional_prompt_carries_the_same_rule(self, provider):
        AIService().converse_professional("Fever of 39 C for two days in a 5-year-old")

        assert "ANSWER THE EXACT QUESTION" in system_prompt_of(provider)


@pytest.mark.django_db
class TestKinyarwandaQuality:
    def test_kinyarwanda_reply_carries_quality_rules_and_glossary(self, provider):
        AIService().converse("mfite umuriro n'inkorora kuva ejo")
        prompt = system_prompt_of(provider)

        assert "KINYARWANDA QUALITY" in prompt
        assert "NEVER repeat" in prompt
        assert "umuriro=fever" in prompt

    def test_english_reply_does_not_carry_kinyarwanda_rules(self, provider):
        AIService().converse("I have had a fever and a cough for two days")

        assert "KINYARWANDA QUALITY" not in system_prompt_of(provider)


def test_multilingual_symptom_analysis():
    rw_text = "Mfite umuriro n'inkorora mu minsi ibiri, kandi ndababara mu gatuza"
    symptoms = SymptomAnalysisService.extract_symptoms(rw_text)

    assert "fever" in symptoms
    assert "cough" in symptoms
    assert "chest pain" in symptoms

    has_emergency = SymptomAnalysisService._check_emergency_keywords(rw_text)
    assert has_emergency is True
