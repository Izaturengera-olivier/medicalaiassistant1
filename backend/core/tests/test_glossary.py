"""Tests for the shared Kinyarwanda medical glossary."""

from core.glossary import expand_query, glossary_compact, matched_terms


def test_kinyarwanda_symptoms_expand_to_english_search_terms():
    expanded = expand_query("mfite umuriro n'inkorora")

    assert "fever" in expanded
    assert "cough" in expanded
    # The original wording is kept so Kinyarwanda content can still match.
    assert expanded.startswith("mfite umuriro n'inkorora")


def test_prefixed_verbs_and_nouns_are_matched_by_stem():
    """Kinyarwanda agglutinates, so 'ndababara mu nda' has no bare word 'inda'."""
    assert "abdominal pain" in expand_query("ndababara mu nda")
    assert "pain" in expand_query("ndumva mbabara umugongo")


def test_english_query_is_left_unchanged():
    query = "interaction risk of metronidazole with warfarin"
    assert expand_query(query) == query
    assert matched_terms(query) == []


def test_glossary_compact_lists_pairs_for_the_prompt():
    compact = glossary_compact()

    assert "umuriro=fever" in compact
    assert "\n" not in compact
