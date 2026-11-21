"""Facility intent reading: a question about one facility gets that fact, not a list.

The six questions below are the ones a live transcript got wrong: a sector
question was answered with a list of health centres, and a correction repeated
the list. They are answered from the register's own columns, so the tests check
the wording as well as the fact.
"""

import pytest

from ai.services.ai_service import AIService
from knowledge.models import AdminPlace, HealthFacility
from knowledge.services import facility_intents as intents


def make_facility(name, facility_type="hospital", **kwargs):
    return HealthFacility.objects.create(
        external_id=f"{name}-{HealthFacility.objects.count()}",
        name=name,
        facility_type=facility_type,
        **kwargs,
    )


def make_place(level, name, **kwargs):
    return AdminPlace.objects.create(
        level=level,
        name=name,
        code=f"{level[:3]}-{kwargs.get('district', '')}-{name}".upper(),
        **kwargs,
    )


@pytest.fixture
def register(db):
    """The Nyabihu slice of the register, including the Rwankeri homonym.

    The real hierarchy has a Rwankeri village in Nyabihu and another in Bugesera.
    The register's own evidence decides which one a patient means: the village
    with a facility named after it.
    """
    make_place("province", "West")
    make_place("district", "Nyabihu", province="West")
    make_place("sector", "Mukamira", province="West", district="Nyabihu")
    make_place(
        "village", "Rwankeri", province="West", district="Nyabihu",
        sector="Mukamira", cell="Rambura",
    )
    make_place("province", "East")
    make_place("district", "Bugesera", province="East")
    make_place("sector", "Musenyi", province="East", district="Bugesera")
    make_place(
        "village", "Rwankeri", province="East", district="Bugesera",
        sector="Musenyi", cell="Rilima",
    )

    make_facility(
        "Rwankeri Hospital",
        district="Nyabihu",
        sector="Mukamira",
        province="Western Province",
        latitude=-1.586181,
        longitude=29.534233,
    )
    for name, sector in (
        ("Kintobo Health Centre", "Kintobo"),
        ("Byakiriba Health Centre", "Rugera"),
        ("Shyira Health Centre", "Rambura"),
        ("Kabatwa Health Centre", "Kabatwa"),
        ("Jomba Health Centre", "Jomba"),
    ):
        make_facility(
            name, facility_type="health_center", district="Nyabihu",
            sector=sector, province="Western Province",
        )
    return HealthFacility.objects.all()


def ask(text, history=None):
    return AIService()._facility_result(text, history or [])


# --- What the wording asks for ----------------------------------------------


@pytest.mark.parametrize(
    "text,intent",
    [
        ("Where is Rwankeri Health Center located? I want the sector.", intents.INTENT_SECTOR),
        ("Which district is Rwankeri Health Center in?", intents.INTENT_DISTRICT),
        ("What services does Rwankeri Health Center provide?", intents.INTENT_SERVICES),
        ("Rwankeri Health Center iherereye mu wuhe murenge?", intents.INTENT_SECTOR),
        ("Find health centers near Rwankeri.", intents.INTENT_NEARBY),
        ("Quel est le secteur de Rwankeri Health Center ?", intents.INTENT_SECTOR),
        ("Où se trouve le centre de santé Rwankeri ?", intents.INTENT_LOCATION),
    ],
)
def test_the_wording_names_the_intent(text, intent):
    question = intents.classify(text)

    assert question is not None
    assert question.intent == intent


@pytest.mark.parametrize(
    "text",
    [
        "I have had a fever and a headache for three days",
        "Ndumva ububabare mu gatuza kandi nkora umuriro",
        "J'ai de la fièvre et des maux de tête depuis trois jours",
    ],
)
def test_a_symptom_message_is_not_a_facility_question(text):
    assert intents.classify(text) is None


def test_a_symptom_sentence_with_an_admin_word_is_not_one_facility_question():
    """A patient describing where they live is not naming a facility."""
    text = "I live in Nyabihu district and have a fever, which health center should I go to?"

    assert intents.classify(text) is None


def test_where_is_the_health_center_in_a_place_stays_a_list():
    assert intents.classify("Where is the health center in Nyabihu?") is None


def test_a_place_question_about_a_known_place_gets_a_list(register):
    result = ask("Where is the health center in Nyabihu?")

    assert result["model_used"] == "health_facility_directory"
    assert result["reply"].startswith("Care facilities in Nyabihu:")


def test_a_lowercase_name_introduced_by_a_connector_is_still_a_name():
    question = intents.classify("the sector of rwankeri health center")

    assert question.intent == intents.INTENT_SECTOR
    assert intents.entity_name("the sector of rwankeri health center")[0] == "rwankeri"


def test_only_an_explicit_denial_counts_as_a_correction():
    first_ask = intents.classify("Where is Rwankeri Health Center located? I want the sector.")
    correction = intents.classify("No, that is not what I asked. I want the sector.")

    assert not first_ask.correction
    assert correction.correction
    assert correction.intent == intents.INTENT_SECTOR


# --- The six questions from the transcript -----------------------------------


def test_a_sector_question_answers_the_sector_not_a_list(register):
    result = ask("Where is Rwankeri Health Center located? I want the sector.")

    assert result["model_used"] == "health_facility_register"
    assert result["reply"].startswith("Rwankeri Hospital is in Mukamira Sector.")
    assert "Care facilities" not in result["reply"]
    assert "\n- " not in result["reply"]


def test_a_nearby_request_still_returns_a_list(register):
    result = ask("Find health centers near Rwankeri.")

    assert result["model_used"] == "health_facility_directory"
    assert result["reply"].startswith("Care facilities near Rwankeri (Nyabihu District):")
    assert "Kintobo Health Centre" in result["reply"]
    assert "Rwankeri Hospital (" not in result["reply"]
    assert len(result["sources"]) >= 3


def test_a_district_question_answers_the_district(register):
    result = ask("Which district is Rwankeri Health Center in?")

    assert result["model_used"] == "health_facility_register"
    assert result["reply"].startswith("Rwankeri Hospital is in Nyabihu District.")


def test_a_services_question_says_the_register_does_not_record_them(register):
    result = ask("What services does Rwankeri Health Center provide?")

    assert result["model_used"] == "health_facility_register"
    assert "does not record which services" in result["reply"]
    assert "Mukamira Sector" in result["reply"]
    # The register has no services column, so any list of services would be invented.
    assert "laboratory" not in result["reply"].lower()
    assert "maternity" not in result["reply"].lower()


def test_kinyarwanda_gets_the_same_verified_sector(register):
    result = ask("Rwankeri Health Center iherereye mu wuhe murenge?")

    assert result["model_used"] == "health_facility_register"
    assert result["reply"].startswith("Rwankeri Hospital iherereye mu murenge wa Mukamira.")


def test_a_correction_uses_the_facility_from_the_patients_own_turn(register):
    history = [
        {"role": "user", "content": "Where is Rwankeri Health Center located?"},
        {
            "role": "assistant",
            "content": "Care facilities in Nyabihu: - Kintobo Health Centre (Kintobo)",
        },
        {"role": "user", "content": "No, that is not what I asked. I want the sector."},
    ]
    result = ask(history[-1]["content"], history[:-1])

    assert result["model_used"] == "health_facility_register"
    assert "Rwankeri Hospital is in Mukamira Sector." in result["reply"]
    assert "Kintobo" not in result["reply"]


def test_a_correction_is_not_answered_about_a_facility_its_wording_resembles(register):
    """The correction's grammar is not a facility name.

    "Non, ce n'est pas…" produces the token "non", which prefixes an unrelated
    row if the sentence is read as a name. The facility to answer about is the
    one from the patient's earlier turn.
    """
    make_facility(
        "Nonko Health Centre", facility_type="health_center", district="Nyabihu",
        sector="Mukamira", province="Western Province",
    )
    history = [
        {"role": "user", "content": "Où se trouve le centre de santé Rwankeri ?"},
        {"role": "assistant", "content": "Rwankeri Hospital se trouve dans le secteur de Mukamira."},
    ]
    result = ask(
        "Non, ce n'est pas ce que j'ai demandé. Je veux le secteur.", history
    )

    assert "Rwankeri Hospital se trouve dans le secteur de Mukamira" in result["reply"]
    assert "Nonko" not in result["reply"]


def test_the_latest_question_wins_over_an_earlier_intent(register):
    history = [
        {"role": "user", "content": "Which district is Rwankeri Health Center in?"},
        {"role": "assistant", "content": "Rwankeri Hospital is in Nyabihu District."},
    ]
    result = ask("And the sector of Rwankeri Health Center?", history)

    assert "Mukamira Sector" in result["reply"]
    assert "Nyabihu District" not in result["reply"]


# --- Honesty about what the register holds -----------------------------------


def test_french_answers_the_same_fact_in_french(register):
    result = ask("Où se trouve le centre de santé Rwankeri ?")

    assert result["model_used"] == "health_facility_register"
    assert "Rwankeri Hospital se trouve dans le secteur de Mukamira" in result["reply"]
    assert "district de Nyabihu" in result["reply"]


def test_an_unknown_facility_is_not_invented(register):
    result = ask("Where is Kigoma Health Center located? I want the sector.")

    assert result["model_used"] == "health_facility_register"
    assert "cannot verify" in result["reply"]
    assert "Kigoma" in result["reply"]
    assert result["sources"] == []
    assert result["follow_up_questions"]


def test_a_name_the_register_spells_differently_is_flagged(register):
    result = ask("Where is Rwankeri Health Center located? I want the sector.")

    assert "Rwankeri Hospital" in result["reply"]
    assert "The register lists it as a hospital, not as a health centre." in result["reply"]


def test_the_six_questions_never_return_a_nearby_list(register):
    for text in (
        "Where is Rwankeri Health Center located? I want the sector.",
        "Which district is Rwankeri Health Center in?",
        "What services does Rwankeri Health Center provide?",
        "Rwankeri Health Center iherereye mu wuhe murenge?",
    ):
        result = ask(text)
        assert result["model_used"] == "health_facility_register", text
        assert "Care facilities" not in result["reply"], text


def test_validation_rejects_an_answer_with_the_wrong_fact(register):
    facility = HealthFacility.objects.get(name="Rwankeri Hospital")
    question = intents.classify("Which district is Rwankeri Health Center in?")

    assert intents.validate_entity_answer(
        "Rwankeri Hospital is in Nyabihu District.", question, [facility]
    )
    assert not intents.validate_entity_answer(
        "Rwankeri Hospital is in Mukamira Sector.", question, [facility]
    )


# --- Wording the 40-question battery got wrong -------------------------------


@pytest.mark.parametrize(
    "text,intent",
    [
        ("Rwankeri Hospital iri mu karere ki?", intents.INTENT_DISTRICT),
        ("Ni mu ntara iyihe irimo Rwankeri Hospital?", intents.INTENT_PROVINCE),
        ("Rwankeri Health Center iherereye mu wuhe murenge?", intents.INTENT_SECTOR),
    ],
)
def test_kinyarwanda_locative_stems_name_the_field(text, intent):
    """Kinyarwanda drops the noun-class vowel after "mu": "akarere" is "karere"."""
    question = intents.classify(text)

    assert question is not None
    assert question.intent == intent


def test_a_kinyarwanda_correction_is_answered_from_the_earlier_facility(register):
    history = [
        {"role": "user", "content": "Rwankeri Health Center iherereye mu wuhe murenge?"},
        {"role": "assistant", "content": "Rwankeri Hospital iherereye mu murenge wa Mukamira."},
    ]
    result = ask("Oya, si icyo nabajije. Nshaka umurenge.", history)

    assert result["model_used"] == "health_facility_register"
    assert "mu murenge wa Mukamira" in result["reply"]
    assert "Kintobo" not in result["reply"]


def test_apostrophe_grammar_is_not_read_as_a_name():
    # "Qu'est-ce" normalises to "qu est ce": three stopwords, not a facility.
    assert intents.entity_name("Qu'est-ce que le centre de santé Rwankeri ?") == (
        "Rwankeri",
        True,
    )


def test_a_lowercase_word_ends_the_name_in_front_of_the_type():
    assert intents.entity_name("Ni mu ntara iyihe irimo Rwankeri Hospital?")[0] == (
        "Rwankeri"
    )


def test_a_french_directions_question_names_the_facility_after_the_preposition():
    text = "Comment aller à Rwankeri Health Center ?"

    assert intents.entity_name(text) == ("Rwankeri", True)
    assert intents.classify(text).intent == intents.INTENT_DIRECTIONS


def test_a_kinyarwanda_province_question_answers_the_translated_province(register):
    """The register stores "Western Province"; the answer names it in Kinyarwanda."""
    result = ask("Ni mu ntara iyihe irimo Rwankeri Hospital?")

    assert result["model_used"] == "health_facility_register"
    assert "mu ntara y'Iburengerazuba" in result["reply"]
    assert "ntibwandika" not in result["reply"]


def test_french_questions_get_the_french_register_answer(register):
    explanation = ask("Qu'est-ce que le centre de santé Rwankeri ?")
    assert explanation["model_used"] == "health_facility_register"
    assert "Rwankeri Hospital est un hôpital" in explanation["reply"]

    services = ask("Quels services offre Rwankeri Health Center ?")
    assert services["model_used"] == "health_facility_register"
    assert "n'indique pas les services fournis" in services["reply"]

    directions = ask("Comment aller à Rwankeri Health Center ?")
    assert directions["model_used"] == "health_facility_register"
    assert "pour l'itinéraire" in directions["reply"]


def test_a_lowercase_facility_name_is_read_when_the_register_has_it(register):
    """Live: "where rwankeri health center located? i want sector" got a list."""
    text = "where rwankeri health center located? i want sector"

    assert intents.classify(text).intent == intents.INTENT_SECTOR
    result = ask(text)
    assert result["model_used"] == "health_facility_register"
    assert result["reply"].startswith("Rwankeri Hospital is in Mukamira Sector.")


def test_a_lowercase_word_the_register_does_not_know_is_not_a_name():
    """The register check is what keeps this from reading "fever" as a facility."""
    assert intents.classify("I have fever, which health center should I go to?") is None
