"""Tests for evidence retrieval over the approved-source corpus."""

import pytest
import requests
from unittest.mock import Mock

from knowledge.models import KnowledgeDocument, MedicalKnowledgeSource
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


def _google_response(*links):
    """A Programmable Search JSON body: title, link and snippet per result."""
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"items": [
        {
            "title": "WHO fever guidance",
            "link": link,
            "snippet": "Fever can have many causes and warning signs need prompt care.",
        }
        for link in links
    ]}
    return response


def _tavily_response():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"results": [{
        "title": "WHO fever advice",
        "url": "https://www.who.int/fever-tavily",
        "content": "Fever in an adult usually needs monitoring and fluids.",
        "score": 0.88,
    }]}
    return response


def enable_google(settings, **overrides):
    settings.WEB_SEARCH_PROVIDER = "google"
    settings.WEB_SEARCH_GOOGLE_API_KEY = "test-key"
    settings.WEB_SEARCH_GOOGLE_ENGINE_ID = "test-engine"
    settings.WEB_SEARCH_ALLOWED_DOMAINS = ["who.int"]
    for key, value in overrides.items():
        setattr(settings, key, value)


def test_google_search_adds_cited_evidence(retrieval_service, settings, monkeypatch):
    enable_google(settings)
    monkeypatch.setattr(
        "knowledge.services.retrieval_service.requests.get",
        lambda *args, **kwargs: _google_response("https://www.who.int/example-fever"),
    )

    results = retrieval_service.retrieve_evidence("fever", max_results=3)

    cited = [item for item in results if item["url"] == "https://www.who.int/example-fever"]
    assert cited
    assert cited[0]["source_name"] == "Approved medical web search"


def test_google_search_asks_for_the_configured_engine(retrieval_service, settings, monkeypatch):
    enable_google(settings)
    sent = {}

    def fake_get(url, params=None, **kwargs):
        sent.update({"url": url, "params": params})
        return _google_response()

    monkeypatch.setattr("knowledge.services.retrieval_service.requests.get", fake_get)

    retrieval_service._search_web("fever", max_results=25)

    assert sent["url"] == "https://www.googleapis.com/customsearch/v1"
    assert sent["params"]["cx"] == "test-engine"
    assert sent["params"]["q"] == "fever"
    # The JSON API refuses a page larger than 10.
    assert sent["params"]["num"] == "10"


def test_google_results_outside_the_trusted_domains_are_dropped(retrieval_service, settings, monkeypatch):
    """The engine's own scope is an admin setting; the allow-list is the contract."""
    enable_google(settings)
    monkeypatch.setattr(
        "knowledge.services.retrieval_service.requests.get",
        lambda *args, **kwargs: _google_response(
            "https://www.who.int/fever",
            "https://apps.who.int/fever",
            "https://moh.gov.rw/fever",
            # A trusted domain used as a prefix, or buried in a query string, is
            # not that domain and must never be shown as approved medical evidence.
            "https://who.int.evil.example/fever",
            "https://evil.example/?redirect=https://who.int",
            "not a url",
        ),
    )

    found = retrieval_service._search_web("fever", max_results=8)

    assert [item["url"] for item in found] == [
        "https://www.who.int/fever",
        "https://apps.who.int/fever",
    ]


def test_a_trusted_domain_written_with_www_or_caps_still_matches(
    retrieval_service, settings, monkeypatch
):
    """Otherwise an admin typing www.who.int silently loses every live citation."""
    enable_google(settings, WEB_SEARCH_ALLOWED_DOMAINS=["www.WHO.int"])
    monkeypatch.setattr(
        "knowledge.services.retrieval_service.requests.get",
        lambda *args, **kwargs: _google_response("https://www.who.int/fever"),
    )

    found = retrieval_service._search_web("fever", max_results=5)

    assert [item["url"] for item in found] == ["https://www.who.int/fever"]


def test_google_search_failure_falls_back_to_the_next_provider(
    retrieval_service, settings, monkeypatch
):
    enable_google(settings, WEB_SEARCH_PROVIDER="google,tavily")
    settings.WEB_SEARCH_API_KEY = "test-key"

    def quota_exceeded(*args, **kwargs):
        raise requests.ConnectionError("quota exceeded")

    monkeypatch.setattr("knowledge.services.retrieval_service.requests.get", quota_exceeded)
    monkeypatch.setattr(
        "knowledge.services.retrieval_service.requests.post",
        lambda *args, **kwargs: _tavily_response(),
    )

    results = retrieval_service._search_web("fever", max_results=3)

    assert [item["url"] for item in results] == ["https://www.who.int/fever-tavily"]


def test_an_unconfigured_google_provider_is_skipped_without_a_call(
    retrieval_service, settings, monkeypatch
):
    """Pasting a Tavily key alone must still work, with no Google request attempted."""
    settings.WEB_SEARCH_PROVIDER = "google,tavily"
    settings.WEB_SEARCH_API_KEY = "test-key"
    settings.WEB_SEARCH_ALLOWED_DOMAINS = ["who.int"]

    def must_not_be_called(*args, **kwargs):
        raise AssertionError("Google search ran without its key and engine ID")

    monkeypatch.setattr("knowledge.services.retrieval_service.requests.get", must_not_be_called)
    monkeypatch.setattr(
        "knowledge.services.retrieval_service.requests.post",
        lambda *args, **kwargs: _tavily_response(),
    )

    found = retrieval_service._search_web("fever", max_results=3)

    assert [item["url"] for item in found] == ["https://www.who.int/fever-tavily"]


def test_no_configured_provider_means_no_network_call(retrieval_service, settings, monkeypatch):
    settings.WEB_SEARCH_PROVIDER = ""

    def must_not_be_called(*args, **kwargs):
        raise AssertionError("a search request left the process without a configured provider")

    monkeypatch.setattr("knowledge.services.retrieval_service.requests.get", must_not_be_called)
    monkeypatch.setattr("knowledge.services.retrieval_service.requests.post", must_not_be_called)

    assert retrieval_service._search_web("fever", max_results=3) == []


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


@pytest.mark.django_db
def test_admin_approved_document_becomes_retrievable():
    """The database, not Python literals, decides what the AI is allowed to cite."""
    source = MedicalKnowledgeSource.objects.create(
        name="Rwanda Biomedical Centre",
        url="https://www.cbr.gov.rw",
        source_type="HOSPITAL",
        approval_status="approved",
    )
    KnowledgeDocument.objects.create(
        source=source,
        document_key="cbr_rabies_post_exposure",
        title="Rabies post-exposure prophylaxis",
        content="Any bite that breaks the skin needs wound washing with soap and water and immediate assessment at a health facility for rabies prophylaxis.",
        url="https://www.cbr.gov.rw",
    )

    results = RetrievalService().retrieve_evidence("dog bite wound rabies")

    assert any(item["title"] == "Rabies post-exposure prophylaxis" for item in results)
    assert any(item["source_name"] == "Rwanda Biomedical Centre" for item in results)
    assert all(item["source_id"] != "" for item in results)


@pytest.mark.django_db
def test_pending_source_documents_never_reach_the_model():
    """AI_SAFETY.md: unapproved documents are filtered before the prompt."""
    source = MedicalKnowledgeSource.objects.create(
        name="Unreviewed Blog Network",
        url="https://example.com",
        source_type="LITERATURE",
        approval_status="pending",
    )
    KnowledgeDocument.objects.create(
        source=source,
        document_key="blog_rabies",
        title="Rabies cured by garlic",
        content="Rabies can be cured at home with garlic.",
        url="https://example.com",
    )

    results = RetrievalService().retrieve_evidence("dog bite wound rabies")

    assert all(item["source_id"] != source.source_key for item in results)


@pytest.mark.django_db
def test_new_common_complaints_have_approved_evidence(retrieval_service):
    """Topics patients here ask about must be answerable from the approved corpus."""
    queries = {
        "coughing blood and losing weight at night": "Tuberculosis",
        "my child breathes fast and the chest pulls in": "Pneumonia",
        "watery diarrhoea with sunken eyes and thirst": "Cholera",
        "sudden weakness on one side and slurred speech": "Stroke",
        "fever with stiff neck and confusion": "Meningitis",
        "dog bite wound washing": "Rabies",
        "burn from hot water at home": "Burns",
        "sad empty feeling for two weeks no pleasure": "Depression",
        "tired pale breathless on exertion": "Anaemia",
    }

    for query, expected in queries.items():
        results = retrieval_service.retrieve_evidence(query, max_results=3)
        assert any(expected in item["title"] for item in results), f"{query} -> {expected}"


@pytest.mark.django_db
def test_deactivating_a_source_removes_it_from_a_new_service():
    """Withdrawing a source stops it being cited without a restart."""
    service = KnowledgeService()
    assert service.verify_source("who")

    assert service.update_source_status("who", "deprecated") is True

    fresh = KnowledgeService()
    assert not fresh.verify_source("who")
    assert fresh.search_knowledge("fever and headache")  # other sources still serve
