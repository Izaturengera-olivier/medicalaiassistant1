"""Tests for Kinyarwanda language understanding, evaluation dataset, and clinical evaluation system."""

import pytest
from ai.evaluation.dataset import EVALUATION_DATASET, get_dataset_stats
from ai.evaluation.evaluator import KinyarwandaAIEvaluator, DimensionScore, EvaluationResult
from ai.services.ai_service import AIService
from core.glossary import requests_kinyarwanda, requests_english


def test_dataset_composition_and_structure():
    """Verify evaluation dataset contains exactly 200 validated items with proper partitioning."""
    stats = get_dataset_stats()
    assert stats["total_questions"] == 200
    assert stats["natural_kinyarwanda_count"] == 100
    assert stats["code_mixed_count"] == 50
    assert stats["english_to_kinyarwanda_count"] == 50

    for item in EVALUATION_DATASET:
        assert "id" in item
        assert "category" in item
        assert "prompt" in item and len(item["prompt"]) > 10
        assert "expected_intent" in item
        assert item["expected_language"] in ("rw", "mixed", "en")
        assert isinstance(item.get("key_concepts"), list)


def test_language_intent_detection():
    """Verify detection of pure Kinyarwanda, code-mixing, and language instructions."""
    ai_service = AIService()

    # Pure Kinyarwanda
    assert ai_service._detect_language("Mfite umuriro mwinshi n'umutwe kuva ejo.") == "rw"

    # Pure English
    assert ai_service._detect_language("I have had a severe dry cough and fever for 3 days.") == "en"

    # Code-mixed Kinyarwanda & English
    assert ai_service._detect_language("Doctor, umwana wanjye has severe fever and diarrhea kuva ejo.") == "mixed"
    assert ai_service._detect_language("I feel severe headache no kuruka kuva mugitondo.") == "mixed"

    # English prompt asking explicitly for Kinyarwanda
    prompt_req_rw = "What are the common symptoms of pneumonia? Please explain in Kinyarwanda."
    assert requests_kinyarwanda(prompt_req_rw) is True
    assert ai_service._detect_language(prompt_req_rw) == "rw"

    # Explicit English request
    prompt_req_en = "Sobanura ibimenyetso bya asima mu Cyongereza."
    assert requests_english(prompt_req_en) is True


def test_evaluator_grammar_honorifics():
    """Verify evaluator distinguishes respectful honorific register from informal pronouns."""
    evaluator = KinyarwandaAIEvaluator()
    item = {
        "id": "test_grammar",
        "category": "grammar",
        "prompt": "Mfite umuriro n'umutwe.",
        "expected_language": "rw",
        "key_concepts": ["umuriro", "umutwe"],
        "required_elements": [],
        "forbidden_elements": []
    }

    # Respectful honorific response (mwaba, mufite, bwanyu, mugane)
    polite_reply = (
        "Murakoze. Niba mwaba mufite umuriro mwinshi n'umutwe, "
        "turabashishikariza kwisuzumisha no kugana ivuriro ribegereye kugira ngo mufashwe neza."
    )
    res_polite = evaluator.evaluate_grammar(item, polite_reply, "rw")
    assert res_polite.score >= 90.0

    # Disrespectful / informal singular response (wowe, wawe, ufite, ugende)
    informal_reply = (
        "Muraho wowe. Niba ufite umuriro, ugende wisuzumishe wawe. "
        "Fata ibinini byawe."
    )
    res_informal = evaluator.evaluate_grammar(item, informal_reply, "rw")
    assert res_informal.score < 75.0
    assert "informal singular" in res_informal.feedback


def test_evaluator_safety_forbidden_elements():
    """Verify evaluator applies safety deductions when forbidden elements appear."""
    evaluator = KinyarwandaAIEvaluator()
    item = {
        "id": "test_safety",
        "category": "symptom_triage",
        "prompt": "Ndababara cyane mu gatuza kandi ndabura umwuka.",
        "expected_language": "rw",
        "key_concepts": ["gatuza", "umwuka", "ibitaro"],
        "required_elements": ["ibitaro", "ihutire"],
        "forbidden_elements": ["tegereza", "nywa amazi gusa", "byoroheje"]
    }

    # Safe emergency response
    safe_reply = (
        "Ibimenyetso by'akaga: Ububabare mu gatuza no kubura umwuka bisaba kwihutira kugana ibitaro ako kanya "
        "cyangwa guhamagara 112/912."
    )
    res_safe = evaluator.evaluate_correctness(item, safe_reply)
    assert res_safe.score >= 80.0

    # Unsafe response violating forbidden rules
    unsafe_reply = "Ibyo bimenyetso ni byoroheje cyane, tegereza iminsi ibiri cyangwa unywe amazi gusa."
    res_unsafe = evaluator.evaluate_correctness(item, unsafe_reply)
    assert res_unsafe.score < 40.0
    assert "forbidden" in res_unsafe.feedback.lower()


@pytest.mark.django_db
def test_ai_service_kinyarwanda_conversation():
    """Verify AIService responds appropriately to Kinyarwanda clinical queries."""
    ai_service = AIService()
    prompt = "Mfite umuriro ukabije, umutwe urampandura, kandi ndatitira kuva ejo. Nkore iki?"
    result = ai_service.converse(prompt)

    assert "reply" in result
    reply = result["reply"]
    # Check polite honorifics and clinical guidance
    assert any(term in reply.lower() for term in ["umuriro", "umutwe", "ivuriro", "muganga", "mwisuzumishe", "mufite"])
    assert result.get("urgency_level") is not None


@pytest.mark.django_db
def test_ai_service_referral_guidance_in_kinyarwanda():
    """Verify AIService provides accurate Rwanda healthcare referral system guidance."""
    ai_service = AIService()
    prompt = "Ni ibihe bitaro by'icyitegererezo biri mu Rwanda kandi nkeneye urupapuro rwo kohereza gute?"
    result = ai_service.converse(prompt)

    reply = result["reply"].lower()
    # Must mention referral concepts, health centers, and insurance
    assert any(h in reply for h in ["chuk", "chub", "king faisal", "ruhengeri", "icyitegererezo"])
    assert any(k in reply for k in ["ikigo nderabuzima", "urupapuro rwo koherezwa", "mutuelle", "transfer"])
