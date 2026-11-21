"""Facility lookup: place matching, distance ranking, dataset hygiene, and the
answer the assistant builds from it."""

import json

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from accounts.models import PatientProfile
from ai.services.ai_service import AIService
from core.constants import UserRole
from knowledge.management.commands.seed_health_facilities import facility_type
from knowledge.models import AdminPlace, HealthFacility
from knowledge.services import facility_service


def make(district, facility_type="hospital", name="Facility", **kwargs):
    return HealthFacility.objects.create(
        external_id=f"{name}-{district}-{facility_type}-{HealthFacility.objects.count()}",
        name=name,
        facility_type=facility_type,
        district=district,
        **kwargs,
    )


def place(level, name, *, province="", district="", sector="", cell="", code=None,
          is_active=True):
    return AdminPlace.objects.create(
        level=level,
        name=name,
        code=code or f"{level[:3]}-{district}{sector}-{name}".upper(),
        province=province,
        district=district,
        sector=sector,
        cell=cell,
        is_active=is_active,
    )


@pytest.fixture
def admin_places(db):
    """A slice of the official hierarchy, in the shapes the resolver must handle.

    The seeder turns the country into 17,441 rows; a test needs the few names it
    types, plus the homonyms that make picking one of them a decision rather than
    whichever row the database happened to return first.
    """
    for name, code in (("Kigali", "P1"), ("North", "P2"), ("South", "P3"), ("West", "P4")):
        place("province", name, code=code)

    for name, province in (
        ("Gasabo", "Kigali"), ("Kicukiro", "Kigali"), ("Nyarugenge", "Kigali"),
        ("Musanze", "North"), ("Burera", "North"),
        ("Huye", "South"), ("Muhanga", "South"),
        ("Karongi", "West"), ("Rubavu", "West"), ("Rusizi", "West"),
    ):
        place("district", name, province=province, code=f"D{name}")

    for name, district in (
        ("Kigali", "Nyarugenge"), ("Muhima", "Nyarugenge"), ("Nyakabanda", "Nyarugenge"),
        ("Muhoza", "Musanze"), ("Kinigi", "Musanze"), ("Muko", "Musanze"),
        ("Huye", "Huye"), ("Gashaki", "Burera"),
        ("Bwishyura", "Karongi"), ("Shyogwe", "Muhanga"),
        ("Gisenyi", "Rubavu"), ("Rubavu", "Rubavu"),
    ):
        place("sector", name, province={"Nyarugenge": "Kigali", "Musanze": "North",
                                        "Burera": "North", "Huye": "South",
                                        "Karongi": "West", "Muhanga": "South",
                                        "Rubavu": "West", "Rusizi": "West"}[district],
              district=district, code=f"S{name}")

    for name, district, sector in (
        ("Nyabugogo", "Nyarugenge", "Kigali"), ("Nyabugogo", "Nyarugenge", "Muhima"),
        ("Huye", "Huye", "Huye"), ("Kibuye", "Karongi", "Bwishyura"),
        ("Gitarama", "Muhanga", "Shyogwe"),
    ):
        place("cell", name, province={"Nyarugenge": "Kigali", "Huye": "South",
                                      "Karongi": "West", "Muhanga": "South"}[district],
              district=district, sector=sector, code=f"C{district}{sector}{name}")

    for name, district, sector, cell in (
        ("Huye", "Rubavu", "Rubavu", "Gisenge"),
        ("Kibuye", "Rusizi", "Rubavu", "Gihundwe"),
        ("Kinyinya", "Musanze", "Kinigi", "Nkotsi"),
        ("Gishaki", "Burera", "Gashaki", "Gashaki"),
        ("Biryogo", "Nyarugenge", "Nyakabanda", "Nyakabanda"),
    ):
        place("village", name, province={"Rubavu": "West", "Rusizi": "West",
                                         "Musanze": "North", "Burera": "North",
                                         "Nyarugenge": "Kigali"}[district],
              district=district, sector=sector, cell=cell, code=f"V{district}{name}")

    return AdminPlace.objects.all()


@pytest.fixture
def facilities(db, admin_places):
    make("Musanze", name="Ruhengeri Referral Hospital", sector="Muhoza",
         province="Northern Province")
    make("Musanze", name="casa", sector="Muko", province="Northern Province")
    make("Musanze", facility_type="health_center", name="Kinigi Health Centre",
         sector="Kinigi", province="Northern Province", latitude=-1.550, longitude=29.600)
    make("Musanze", facility_type="pharmacy", name="Muhoza Pharmacy", sector="Muhoza",
         province="Northern Province")
    make("Huye", name="CHUB Teaching Hospital", sector="Ngoma")
    make("Huye", name="Kabutare District Hospital", sector="Ngoma")
    make("Gasabo", facility_type="clinic", name="Remera Clinic", province="Kigali City",
         sector="Remera")
    make("Gasabo", facility_type="pharmacy", name="2050 Pharmacy", province="Kigali City",
         sector="Gisozi")
    make("Gasabo", facility_type="pharmacy", name="2050PHARMACY", province="Kigali City",
         sector="Gisozi")
    make("Nyarugenge", facility_type="health_center", name="Nyabugogo Health Centre",
         province="Kigali City", sector="Muhima")
    make("Nyarugenge", name="Biryogo Hospital", province="Kigali City", sector="Nyarugenge")
    make("Nyarugenge", name="Nyarugenge District Hospital", province="Kigali City",
         sector="Nyarugenge")
    make("Rubavu", name="EDF", sector="Gisenyi")
    make("Rubavu", name="Rubavu District Hospital", sector="Rubavu", latitude=-1.703,
         longitude=29.262)
    make("Rubavu", name="Gisenyi Health Centre", facility_type="health_center",
         sector="Gisenyi", latitude=-1.679, longitude=29.256)
    return HealthFacility.objects.all()


def test_asks_are_recognised_in_all_three_languages(facilities):
    assert facility_service.is_facility_question("where is the nearest hospital")
    assert facility_service.is_facility_question("hospital i Musanze")
    assert facility_service.is_facility_question("pharmacie hafi ya Kigali")
    assert facility_service.is_facility_question("ni hehe ivuriro riri hafi ya Rubavu")


def test_symptom_questions_do_not_become_a_facility_list(facilities):
    assert not facility_service.is_facility_question("I have a fever and a headache for three days")
    assert facility_service.asked_kind("I have a fever and a headache for three days") is None


def test_asking_when_to_see_a_doctor_is_not_a_facility_lookup(facilities):
    """Live bug: "nagomba kugana umuganga" (should I see a doctor) was read as a
    clinic request, and the homonym "Nkora" then produced a clinic list."""
    text = (
        "Mfite umuriro n inkorora iminsi itatu. Nkora iki, kandi ni ryari "
        "nagomba kugana umuganga?"
    )

    assert facility_service.asked_kind(text) is None
    assert not facility_service.is_facility_question(text)


def test_a_word_of_the_message_finds_the_official_unit_it_names(facilities):
    assert [(p.level, p.name) for p in facility_service.resolve_places("hospital i Musanze")] == [
        ("district", "Musanze")
    ]
    assert facility_service.resolve_places("I feel tired") == []


@pytest.mark.parametrize(
    "text,expected_place,expected_level",
    [
        ("hospital i Musanze", "Musanze", "district"),
        ("clinics in Kigali", "Kigali City", "province"),
        ("ibitaro i Nyabugogo", "Nyarugenge", "district"),
    ],
)
def test_place_matching_lands_on_the_area_the_register_can_search(
    facilities, text, expected_place, expected_level
):
    found = facility_service.search(text)

    assert found.place == expected_place
    assert found.place_level == expected_level


@pytest.mark.parametrize(
    "text,expected",
    [
        ("hospital i Musanze", "Ruhengeri Referral Hospital"),
        ("Musanze hospital", "Ruhengeri Referral Hospital"),
        ("ivuriro i Musanze", "Kinigi Health Centre"),
        ("pharmacie muri Kigali", "2050 Pharmacy"),
        ("ibitaro bya Huye", "CHUB Teaching Hospital"),
    ],
)
def test_named_place_returns_a_facility_of_the_asked_kind(facilities, text, expected):
    found = facility_service.search(text)

    assert found.has_results
    assert found.results[0]["name"] == expected


def test_a_place_without_a_name_or_coordinates_is_not_answered(facilities):
    found = facility_service.search("where is the nearest hospital")

    assert not found.anchored
    assert not found.has_results


def test_mapped_non_facilities_are_never_suggested(facilities):
    names = [row["name"] for row in facility_service.search("hospital i Rubavu").results]

    assert "EDF" not in names
    assert "Rubavu District Hospital" in names


def test_the_same_pharmacy_entered_twice_is_listed_once(facilities):
    names = [row["name"] for row in facility_service.search("pharmacy in Kigali").results]

    assert names.count("2050 Pharmacy") == 1
    assert "2050PHARMACY" not in names


def test_coordinates_rank_by_real_distance(facilities):
    # Gisenyi town centre: the closer place must lead, whatever type it is.
    found = facility_service.search("nearest place to get care", latitude=-1.68, longitude=29.26)

    assert [row["name"] for row in found.results][:2] == ["Gisenyi Health Centre", "Rubavu District Hospital"]
    assert found.results[0]["distance_km"] < found.results[1]["distance_km"]
    assert found.results[0]["maps_url"].startswith("https://www.google.com/maps/")


def test_an_asked_type_still_filters_when_ranking_by_distance(facilities):
    found = facility_service.search("hospital near me", latitude=-1.68, longitude=29.26)

    assert [row["type"] for row in found.results] == ["hospital"]
    assert found.results[0]["name"] == "Rubavu District Hospital"


def test_a_district_name_resolves_to_the_district_not_its_homonyms(facilities):
    """"Huye" is a district, a sector, a cell and a village in Rubavu.

    "ibitaro bya Huye" asks for the district's hospitals: the name of a district
    means the district, whatever else the hierarchy carries under the same word.
    """
    found = facility_service.search("ibitaro bya Huye")

    assert found.place == "Huye"
    assert {row["district"] for row in found.results} == {"Huye"}


def test_a_city_is_not_answered_with_the_one_sector_sharing_its_name(facilities):
    """"Kigali" is the city and a small sector in Nyarugenge.

    Taking the sector would answer a question about the whole capital with the two
    pharmacies on one hill in its centre.
    """
    found = facility_service.search("hospital in Kigali")

    assert found.place_level == "province"
    assert {row["district"] for row in found.results} <= {"Gasabo", "Kicukiro", "Nyarugenge"}


def test_a_village_is_searched_as_the_area_holding_it(facilities):
    # The facility register files a place by sector, district and province and
    # knows no villages, so a village is answered from the sector around it.
    for name in ("Kinyinya", "Nkotsi", "Shyringo"):
        make("Musanze", facility_type="health_center", name=f"{name} Health Centre",
             sector="Kinigi", province="Northern Province")

    found = facility_service.search("ivuriro riri Kinyinya")

    assert found.locality == "Kinyinya"
    assert found.place == "Kinigi"
    assert found.place_level == "sector"


def test_a_cell_shared_by_two_sectors_is_searched_as_one_area(facilities):
    # Nyabugogo is a cell in sector Kigali and a cell in sector Muhima: the
    # patient means the place, and the answer must not repeat itself per copy.
    found = facility_service.search("hospital i Nyabugogo")

    assert found.locality == "Nyabugogo"
    assert found.place == "Nyarugenge"
    assert [row["name"] for row in found.results if row["name"] == "Biryogo Hospital"] == [
        "Biryogo Hospital"
    ]


def test_a_name_used_in_two_districts_follows_the_facility_named_for_it(facilities):
    # Kibuye is a cell in Karongi and a village in Rusizi, and people call the
    # town by its old name because Kibuye Referral Hospital stands there.
    make("Karongi", name="Kibuye Referral Hospital", sector="Bwishyura")
    make("Rusizi", name="Rusizi District Hospital", sector="Rusizi")

    found = facility_service.search("hospital i Kibuye")

    assert found.locality == "Kibuye"
    assert found.results[0]["name"] == "Kibuye Referral Hospital"
    assert "Rusizi District Hospital" not in [row["name"] for row in found.results]


def test_a_place_with_too_little_mapped_widens_instead_of_answering_nothing(facilities):
    # One health centre is an answer about a hill, not a choice of care.
    found = facility_service.search("ivuriro i Kinigi")

    assert found.locality == "Kinigi"
    assert found.place == "Musanze"
    assert found.results


def test_a_place_the_register_has_never_heard_of_widens_to_the_province(facilities):
    found = facility_service.search("hospital i Gishaki")

    assert found.locality == "Gishaki"
    assert found.place == "Northern Province"
    assert found.results


def test_a_widened_search_starts_where_the_patient_stands(facilities):
    # Kinigi has one mapped place, so the district gets searched; the list must
    # still begin at Kinigi rather than at the busiest end of Musanze - and the
    # centre it was ordered around is never printed as a distance.
    make("Musanze", facility_type="health_center", name="Musanze Referral Health Centre",
         sector="Muhoza", province="Northern Province", latitude=-1.499, longitude=29.635)

    found = facility_service.search("ivuriro riri hafi ya Kinigi")

    assert found.locality == "Kinigi"
    assert found.results[0]["name"] == "Kinigi Health Centre"
    assert [row["distance_km"] for row in found.results] == [None, None]


def test_a_widened_list_never_shows_a_distance_as_if_it_were_measured(facilities):
    found = facility_service.search("hospital i Musanze")

    assert found.results
    assert all(row["distance_km"] is None for row in found.results)


@pytest.mark.parametrize(
    "text", ["hospital in Northern Province", "ibitaro byo mu ntara y'amajyaruguru"]
)
def test_a_province_is_reached_by_the_words_patients_use(facilities, text):
    found = facility_service.search(text)

    assert found.place == "Northern Province"
    assert found.results


def test_a_deactivated_place_stops_matching(facilities):
    AdminPlace.objects.filter(name="Musanze").update(is_active=False)

    found = facility_service.search("hospital i Musanze")

    assert found.place is None
    assert not found.results


def test_facility_answer_cites_each_place_it_names(facilities):
    result = AIService()._facility_result("hospital i Musanze", [])

    assert result is not None
    assert result["model_used"] == "health_facility_directory"
    assert "Ruhengeri Referral Hospital" in result["reply"]
    assert "[1]" in result["reply"]
    assert result["sources"][0]["name"] == "Ruhengeri Referral Hospital"
    assert result["sources"][0]["url"].startswith("https://www.google.com/maps/")
    assert "casa" not in result["reply"]


def test_facility_answer_is_in_the_language_of_the_question(facilities):
    rw = AIService()._facility_result("ibitaro bya hafi i Musanze", [])
    en = AIService()._facility_result("which hospitals are in Musanze", [])

    assert rw["reply"].startswith("Amavuriro n'ibitaro biri i Musanze:")
    assert "Ibitaro" in rw["reply"]
    assert en["reply"].startswith("Care facilities in Musanze:")


def test_an_answer_widened_past_the_place_named_says_where_it_searched(facilities):
    # The patient named a sector, the list came from the district around it, and
    # hiding that would leave them ruling the far end of the district out.
    en = AIService()._facility_result("health centre near Muhima", [])
    rw = AIService()._facility_result("ivuriro riri hafi ya Nyabugogo", [])

    assert en["reply"].startswith("Care facilities near Muhima (Nyarugenge District):")
    assert rw["reply"].startswith("Ahantu ho kuvurirwa hafi ya Nyabugogo (mu karere ka Nyarugenge):")


def test_a_district_with_only_a_poorly_named_row_still_gets_an_answer(facilities):
    HealthFacility.objects.filter(district="Musanze").delete()
    make("Musanze", name="casa", sector="Muko")

    found = facility_service.search("hospital i Musanze")

    assert [row["name"] for row in found.results] == ["casa"]


def test_emergency_symptoms_keep_the_triage_warning(facilities):
    result = AIService()._facility_result(
        "I have chest pain and difficulty breathing, which hospital is near Musanze", []
    )

    assert result["warning_signs"]
    assert "emergency care now" in result["reply"]
    assert result["urgency_level"] != "INFORMATIONAL"


def test_facility_question_never_reaches_the_llm(facilities, monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("facility answers must not spend provider tokens")

    monkeypatch.setattr("ai.providers.requests.post", explode)
    service = AIService()
    monkeypatch.setattr(service, "_use_llm_provider", lambda: True)

    result = service.converse("hospital i Musanze", history=[])

    assert result["model_used"] == "health_facility_directory"
    assert "Ruhengeri Referral Hospital" in result["reply"]


def test_a_symptom_message_never_reads_the_place_or_facility_tables(db):
    """The provider-mocked conversation tests have no database access.

    Doing the facility lookup for every message broke them, so the decision to
    look one up has to be made from the words alone.
    """
    with CaptureQueriesContext(connection) as queries:
        result = AIService()._facility_result(
            "I have had a fever and a headache for three days", []
        )

    assert result is None
    sql = [q["sql"] for q in queries.captured_queries]
    assert not [statement for statement in sql if "health_facilities" in statement]
    assert not [statement for statement in sql if "admin_places" in statement]


@pytest.mark.parametrize(
    "properties,expected",
    [
        ({"name": "Ruhengeri Referral Hospital", "amenity": "hospital"}, "hospital"),
        ({"name": "Clinic Horana Ubuzima Ltd", "amenity": "hospital"}, "clinic"),
        ({"name": "Kinigi Health Centre", "amenity": "hospital"}, "health_center"),
        ({"name": "Bungwe Health Post", "amenity": "hospital"}, "health_post"),
        ({"name": "Muhoza Pharmacy", "amenity": "pharmacy"}, "pharmacy"),
        ({"name": "Ruli Sector", "amenity": "hospital"}, "other"),
        ({"name": "APAPER Primary School", "amenity": "hospital"}, "other"),
    ],
)
def test_a_row_is_labelled_by_its_name_not_by_its_osm_tag(properties, expected):
    assert facility_type(properties) == expected


def test_the_hierarchy_seeder_writes_one_row_per_unit(tmp_path, db):
    """Villages are the grain of the dataset, so a unit repeats hundreds of times.

    A sector code is kept as the text "0101": the leading zeros are part of the
    official code, and an integer would silently drop them.
    """
    def record(cell, cell_code, village="ACYR", village_code="01010101"):
        return {
            "province_code": 1, "province_name": "KIGALI",
            "district_code": 12, "district_name": "Gasabo",
            "sector_code": "0101", "sector_name": "Gasabo",
            "cell_code": cell_code, "cell_name": cell,
            "village_code": village_code, "village_name": village,
        }

    path = tmp_path / "places.json"
    path.write_text(
        json.dumps([record("Kimisambu", "010101"), record("Kacyiru", "010102")]),
        encoding="utf-8",
    )
    call_command("seed_admin_places", file=str(path))

    assert sorted(
        (row.level, row.name) for row in AdminPlace.objects.all()
    ) == [
        ("cell", "Kacyiru"), ("cell", "Kimisambu"),
        ("district", "Gasabo"), ("province", "Kigali"),
        ("sector", "Gasabo"), ("village", "ACYR"),
    ]
    village = AdminPlace.objects.get(level="village")
    assert (village.province, village.district, village.sector, village.cell) == (
        "Kigali", "Gasabo", "Gasabo", "Kimisambu"
    )
    assert AdminPlace.objects.get(level="sector").code == "0101"
    assert AdminPlace.objects.get(level="province").name_key == "kigali"

    call_command("seed_admin_places", file=str(path))
    assert AdminPlace.objects.count() == 6


def test_the_seeder_leaves_a_seeded_database_alone_when_asked(tmp_path, db):
    place("district", "Musanze", province="North", code="D-existing")
    path = tmp_path / "places.json"
    path.write_text(json.dumps([{"province_code": 1, "province_name": "WEST"}]), encoding="utf-8")

    call_command("seed_admin_places", file=str(path), if_empty=True)

    assert [row.name for row in AdminPlace.objects.all()] == ["Musanze"]


@pytest.fixture
def api_client(db):
    user = get_user_model().objects.create_user(
        email="lost@example.com",
        first_name="Aline",
        last_name="Uwase",
        role=UserRole.PATIENT,
        password="SecurePass123!",
    )
    PatientProfile.objects.create(user=user)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_the_endpoint_answers_a_location_from_the_coordinates_sent_by_the_device(
    api_client, facilities
):
    response = api_client.post(
        "/api/ai/analyze-symptoms/",
        {"patient_input": "I need a hospital", "latitude": -1.68, "longitude": 29.26},
        format="json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reply"].startswith("The facilities closest to you:")
    assert "Rubavu District Hospital" in body["reply"]
    assert body["sources"][0]["url"].startswith("https://www.google.com/maps/")


def test_the_endpoint_rejects_a_coordinate_outside_the_country(api_client, facilities):
    response = api_client.post(
        "/api/ai/analyze-symptoms/",
        {"patient_input": "nearest hospital", "latitude": 95.0, "longitude": 29.26},
        format="json",
    )

    assert response.status_code == 400
    assert "latitude" in response.json()


def test_the_answer_names_the_neighbourhood_the_patient_wrote(facilities):
    result = AIService()._facility_result(
        "ndi nyabugogo ni irihe vuriro rinyegereye ko numva ntameze neza", []
    )

    assert result is not None
    assert result["reply"].startswith(
        "Ahantu ho kuvurirwa hafi ya Nyabugogo (mu karere ka Nyarugenge):"
    )
    assert "location" in result["recommended_next_step"]


def test_a_near_me_question_with_no_place_asks_where_the_patient_is(facilities):
    result = AIService()._facility_result("which hospital is nearest to me", [])

    assert result is not None
    assert "tell me where you are" in result["reply"]
    assert result["follow_up_questions"]


def test_device_coordinates_do_not_reorder_a_place_the_patient_named(facilities):
    """Live bug: "which health centre near me in Gakenke" was answered with the
    district's facilities ranked from the phone's fix 30 km away, so every row
    read "25.7 km" and the named district was lost in the noise."""
    found = facility_service.search(
        "health centres in Musanze", latitude=-1.68, longitude=29.26
    )

    assert found.place == "Musanze"
    assert found.coordinates is None
    assert all(row["distance_km"] is None for row in found.results)


def test_a_named_place_wins_over_a_device_fix_and_says_so(facilities):
    result = AIService()._facility_result(
        "am at Musanze which health centre near me?", [],
        latitude=-1.68, longitude=29.26,
    )

    assert result is not None
    assert result["reply"].startswith("Care facilities in Musanze:")
    assert "km" not in result["reply"]
    assert "Name the sector or cell" in result["recommended_next_step"]


def test_a_row_named_after_an_admin_unit_is_not_a_hospital(facilities):
    """Live bug: "Ruli Sector" is filed by OSM as a hospital beside Ruli District
    Hospital, and was listed to the patient as a place to get care."""
    make("Musanze", name="Ruli Sector", sector="Ruli")

    names = [row["name"] for row in facility_service.search("hospital i Musanze").results]

    assert "Ruli Sector" not in names
    assert "Ruhengeri Referral Hospital" in names


def test_a_follow_up_takes_the_place_and_type_from_the_patients_own_turns(facilities):
    """"i need one near me" after "which health centre?" means a health centre in
    the district the patient named, not another mixed list."""
    history = [
        {"role": "user", "content": "list health centres in Musanze"},
        {"role": "assistant", "content": "Care facilities in Musanze:\n- Kinigi Health Centre (Health Centre, Kinigi, Musanze) [1]"},
        {"role": "user", "content": "am at Musanze which health centre near me?"},
        {"role": "assistant", "content": "Care facilities in Musanze:\n- Kinigi Health Centre (Health Centre, Kinigi, Musanze) [1]"},
    ]

    result = AIService()._facility_result("i need one near me", history)

    assert result is not None
    assert result["reply"].startswith("Care facilities in Musanze (from your earlier message):")
    assert "Ruhengeri Referral Hospital" not in result["reply"]
    assert [source["name"] for source in result["sources"]] == ["Kinigi Health Centre"]
    assert "Share your location" in result["recommended_next_step"]


def test_place_names_inside_an_earlier_answer_do_not_anchor_the_next_question(facilities):
    """Live bug: the assistant's list contained "Coko Health Centre" and
    "Rwankuba health centre", and the next question was headed "near Coko,
    Rwankuba" instead of the Gakenke the patient had typed."""
    history = [
        {"role": "user", "content": "health centres in Musanze"},
        {"role": "assistant", "content": "The nearest one is on the hill in Gishaki."},
    ]

    result = AIService()._facility_result("i need one near me", history)

    assert result is not None
    assert result["reply"].startswith("Care facilities in Musanze (from your earlier message):")
