"""Tests for evidence retrieval over the approved-source corpus."""

import pytest
from unittest.mock import Mock

from knowledge.services import KnowledgeService, RetrievalService


@pytest.fixture
def retrieval_service():
    return RetrievalService()


def test_multi_word_sentence_query_matches_relevant_document(retrieval_service):
    """A realistic sentence must match on token overlap, not substring equality."""
    results = retrieval_service.retrieve_evidence("I have had a fever and a headache for two days")

    assert results, "expected evidence for a common symptom description"
    titles = [item["title"] for item in results]
    assert any("Fever" in title or "Headache" in title for title in titles)


def test_malaria_query_returns_malaria_document(retrieval_service):
    results = retrieval_service.retrieve_evidence("fever with chills and sweating")

    assert results
    assert results[0]["title"] == "Malaria Signs and When to Seek Care"


def test_back_pain_query_returns_related_evidence_only(retrieval_service):
    results = retrieval_service.retrieve_evidence("I have pain in my back")

    titles = [item["title"] for item in results]
    assert any("Back Pain" in title for title in titles)
    assert not any("Headache" in title for title in titles)
    assert not any("Malaria" in title for title in titles)


def test_evidence_carries_trusted_source_metadata(retrieval_service):
    results = retrieval_service.retrieve_evidence("fever")

    assert results
    top = results[0]
    assert top["source_name"] in {"World Health Organization", "Rwanda Ministry of Health"}
    assert top["source_type"] in {"WHO", "MOH"}
    assert top["url"].startswith("https://")
    assert top["relevance_score"] > 0
    assert top["content"]


def test_unrelated_query_returns_no_evidence(retrieval_service):
    assert retrieval_service.retrieve_evidence("quantum chromodynamics Lagrangian") == []


def test_results_respect_max_results(retrieval_service):
    results = retrieval_service.retrieve_evidence("fever headache cough", max_results=2)
    assert len(results) <= 2


def test_evidence_comes_only_from_approved_sources(retrieval_service):
    knowledge_service = KnowledgeService()
    knowledge_service.add_source({
        "id": "untrusted_blog",
        "name": "Random Health Blog",
        "url": "https://example.com",
        "source_type": "LITERATURE",
        "approval_status": "pending",
    })
    knowledge_service.add_document({
        "id": "doc_pending",
        "title": "Fever cures from the internet",
        "content": "Fever can be cured with this one weird trick.",
        "source_id": "untrusted_blog",
        "url": "https://example.com",
    })

    approved_ids = {source["id"] for source in retrieval_service.knowledge_service.get_approved_sources()}
    assert "untrusted_blog" not in approved_ids
    for item in retrieval_service.retrieve_evidence("fever"):
        assert item["source_id"] in approved_ids


def test_format_evidence_for_ai_includes_source_and_url(retrieval_service):
    results = retrieval_service.retrieve_evidence("fever")
    formatted = retrieval_service.format_evidence_for_ai(results)

    assert results[0]["source_name"] in formatted
    assert results[0]["url"] in formatted


def test_configured_web_search_adds_cited_evidence(retrieval_service, settings, monkeypatch):
    settings.WEB_SEARCH_PROVIDER = "tavily"
    settings.WEB_SEARCH_API_KEY = "test-key"
    settings.WEB_SEARCH_ALLOWED_DOMAINS = ["who.int"]

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "results": [{
            "title": "WHO fever guidance",
            "url": "https://www.who.int/example-fever",
            "content": "Fever can have many causes and warning signs need prompt care.",
            "score": 0.91,
        }]
    }
    monkeypatch.setattr("knowledge.services.retrieval_service.requests.post", lambda *args, **kwargs: response)

    results = retrieval_service.retrieve_evidence("fever", max_results=1)

    assert any(item["url"] == "https://www.who.int/example-fever" for item in results)


def test_kinyarwanda_query_retrieves_english_evidence(retrieval_service):
    """Approved sources publish in English, so the query has to be expanded first."""
    results = retrieval_service.retrieve_evidence("mfite umuriro n'inkorora")

    assert results
    assert any("Fever" in item["title"] or "Cough" in item["title"] for item in results)


def test_formatted_evidence_is_numbered_for_inline_citation(retrieval_service):
    results = retrieval_service.retrieve_evidence("fever")
    formatted = retrieval_service.format_evidence_for_ai(results)

    assert "[1]" in formatted
    assert "[2]" in formatted or len(results) == 1


def test_formatted_evidence_keeps_enough_content_to_ground_an_answer(retrieval_service):
    results = retrieval_service.retrieve_evidence("fever")
    formatted = retrieval_service.format_evidence_for_ai(results)

    top_content = results[0]["content"]
    expected = top_content[: retrieval_service.EVIDENCE_CONTENT_CHARS]
    assert expected in formatted
