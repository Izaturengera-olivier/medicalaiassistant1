"""Evidence capacity: the model needs enough source text to explain things deeply.

Measured on the live corpus: all 38 approved documents are 241-995 characters, so
the per-passage cap must not clip an approved document, while live web-search
passages (which arrive at up to 4000 characters) still need bounding.
"""

import pytest

from knowledge.models import KnowledgeDocument, MedicalKnowledgeSource
from knowledge.services import RetrievalService


@pytest.mark.django_db
def test_cap_never_clips_the_longest_approved_document():
    service = RetrievalService()
    longest = max(len(doc.content) for doc in KnowledgeDocument.objects.all())

    assert longest <= service.EVIDENCE_CONTENT_CHARS, (
        "raising EVIDENCE_CONTENT_CHARS past the corpus is pointless, lowering it "
        "silently deletes grounding material"
    )


@pytest.mark.django_db
def test_full_approved_document_content_reaches_the_prompt():
    service = RetrievalService()
    results = service.retrieve_evidence("fever with stiff neck", max_results=8)
    assert results

    formatted = service.format_evidence_for_ai(results)
    for item in results:
        assert (item["content"] or "").strip() in formatted


@pytest.mark.django_db
def test_long_web_passage_is_bounded_not_dumped():
    """A 4000-character live passage must be cut to the cap, keeping the prompt affordable."""
    service = RetrievalService()
    content = "Fever guidance. " * 400  # ~6000 characters
    formatted = service.format_evidence_for_ai(
        [{
            "title": "WHO fever page",
            "content": content,
            "source_name": "World Health Organization",
            "url": "https://www.who.int/fever",
        }]
    )

    assert content[: service.EVIDENCE_CONTENT_CHARS] in formatted
    assert content[: service.EVIDENCE_CONTENT_CHARS + 20] not in formatted


@pytest.mark.django_db
def test_widened_window_reaches_the_prompt_block():
    """More passages means more material to explain, so the block must carry them all."""
    source = MedicalKnowledgeSource.objects.filter(approval_status="approved").first()
    for index in range(9):
        KnowledgeDocument.objects.create(
            source=source,
            document_key=f"depth_probe_headache_{index}",
            title=f"Headache guidance variant {index}",
            content=(
                "Headache with neck stiffness and fever needs urgent assessment for "
                "meningitis; tension headache improves with rest and hydration."
            ),
            url="https://www.moh.gov.rw/headache",
        )

    service = RetrievalService()
    results = service.retrieve_evidence("headache neck stiffness fever", max_results=8)

    assert len(results) >= 3
    assert len(results) <= 8
    formatted = service.format_evidence_for_ai(results)
    assert f"[{len(results)}]" in formatted
