"""Deterministic "where do I get care" answers, using the HealthFacility table.

Facility names are facts a model should never have to recall, so this answers from
the database instead of the LLM: it is exact, it still works when the provider is
rate limited or down, and it costs no tokens.
"""

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Q

from knowledge.models import AdminPlace, HealthFacility

# The facility type a patient asked for, in the three languages the app answers in.
KIND_WORDS: Dict[str, Tuple[str, ...]] = {
    "hospital": ("hospital", "hopital", "hôpital", "ibitaro", "referral hospital", "teaching hospital"),
    "health_center": ("health centre", "health center", "ivuriro", "vuriro"),
    "health_post": ("health post", "poste de sante", "poste de santé"),
    # "umuganga" (doctor) and "umutanga" (provider) name a person, not a place:
    # a symptom question asking when to see one must reach the model instead.
    "clinic": ("clinic", "clinique", "polyclinique", "policlinique", "kliniki"),
    "pharmacy": ("pharmacy", "pharmacie", "farumasi", "drugstore", "drug store"),
}

# Words that mean "closest to me", which is a ranking request, not a type.
# "egereye" is the stem of "rinyegereye" / "byegereye" / "cyegereye" (near it).
NEARBY_WORDS = (
    "near", "nearby", "nearest", "close to", "closest",
    "hafi", "kuruta", "egereye",
    "proximité", "proximite",
)

# Kinyarwanda "where is" / "which is" question words that precede a facility type.
# "ni irihe" = "which is", "ni hehe" = "where is", "iri he" = "where is it"
_RW_WHERE_PATTERNS = re.compile(
    r"\b(ni irihe|ni hehe|iri he|irihe|hehe|ndi|nkiri|ntuye|ntuye i|ndi i)\b",
    re.I,
)

# The register holds the whole country, but a patient is asked to name a place in
# the words they know: a village, a cell, a sector. AdminPlace resolves any of
# those to the district and sector the facility rows can be filtered on, so
# matching is driven by the official hierarchy rather than by a hand-written list.
LEVEL_TIGHTNESS = {"village": 0, "cell": 1, "sector": 2, "district": 3, "province": 4}

# The hierarchy spells the provinces short ("Kigali", "South"), the facility
# register spells them out ("Kigali City", "Southern Province").
PROVINCE_REGISTER_NAMES = {
    "Kigali": "Kigali City",
    "North": "Northern Province",
    "South": "Southern Province",
    "East": "Eastern Province",
    "West": "Western Province",
}

# Other ways the provinces get written, matched inside the message rather than as a
# whole word: the Kinyarwanda names, which arrive with a prefix ("intara
# y'amajyepfo"), and the English adjectives copied off a map ("Northern Province").
# A province written as its own name ("North", "Kigali") needs no entry here.
PROVINCE_WORDS = {
    "amajyaruguru": "North",
    "northern": "North",
    "amajyepfo": "South",
    "southern": "South",
    "iburasirazuba": "East",
    "eastern": "East",
    "iburengerazuba": "West",
    "western": "West",
}

# One or two rows is an answer about a hill, not an area to choose from: a match
# narrower than the register is widened to the level above until it can offer a
# real choice, and the reply names the level it settled on.
MIN_FACILITIES_FOR_AN_AREA = 3

TYPE_PRIORITY = {
    "hospital": 0,
    "health_center": 1,
    "clinic": 2,
    "health_post": 3,
    "pharmacy": 4,
    "other": 5,
}

# OpenStreetMap maps what a surveyor saw, not what a patient can use: a primary
# school, an electricity office and a church hall carry amenity=hospital here.
# 6 of the 1333 rows match, and an admin can deactivate any row instead.
NOT_A_FACILITY = re.compile(
    r"school|nursery|church|mosque|stadium|airport|bank|market|"
    r"electricity|electricite|électricité|sector office|edf",
    re.I,
)

# Names that read as a facility in one of the three languages the app answers in.
FACILITY_IN_NAME = re.compile(
    r"hospital|ibitaro|health cent|health post|ivuriro|clinique|clinic|pharmacie|"
    r"pharmacy|farumasi|medical|centre|center|maternite|maternity|police|chuk|chub|chrr|rbc",
    re.I,
)


@dataclass
class FacilitySearch:
    """What the question asked for and what the database could offer."""

    # The area the database actually searched, which is the place the patient named
    # widened to the level that has facilities mapped in it.
    place: Optional[str] = None
    place_level: Optional[str] = None
    # The place as the patient wrote it, which is what to call them back to: someone
    # standing in Nyabugogo scanning a list headed "Kigali" finds no comfort in it,
    # so the reply names their word and shows the searched area beside it.
    locality: Optional[str] = None
    kind: Optional[str] = None
    coordinates: Optional[Tuple[float, float]] = None
    results: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def anchored(self) -> bool:
        """Whether "near" has anything to mean: a named place or coordinates."""
        return bool(self.place) or self.coordinates is not None

    @property
    def has_results(self) -> bool:
        return bool(self.results)


def asked_kind(text: str) -> Optional[str]:
    lowered = (text or "").lower()
    for kind, words in KIND_WORDS.items():
        if any(word in lowered for word in words):
            return kind
    return None


def mentions_facility(text: str) -> bool:
    """Cheap lexical pre-check that needs no database.

    Matching a place name means reading the place hierarchy and the facility table,
    so this decides whether that is worth doing: a symptom message never reaches it.
    """
    lowered = (text or "").lower()
    if bool(asked_kind(lowered)):
        return True
    return any(word in lowered for word in NEARBY_WORDS)


def is_facility_question(text: str) -> bool:
    """True when the patient asks where to get care rather than what is wrong.

    Deliberately narrow, so "why does my head hurt" still reaches the model and
    only "where is the nearest hospital" or "hospital i Musanze" comes here.
    """
    lowered = (text or "").lower()

    # Informational or clinical queries asking "which symptoms", "what causes",
    # "which referral hospital", "how to treat", "should I take", etc. are clinical CDS questions, never facility lookups.
    clinical_query_patterns = (
        "which symptom", "what symptom", "which symptoms", "what symptoms",
        "which referral", "what referral", "which refferal", "what refferal",
        "is there a referral", "are there referral", "which is the referral",
        "what is the referral", "referral hospital in", "refferal hospital in",
        "icyitegererezo", "icyitegerezo", "ibitaro by'icyitegererezo", "ibitaro byicyitegererezo",
        "ibihe bimenyetso", "ni ibihe bimenyetso", "ibimenyetso by'akaga bisaba",
        "why do", "why does", "why would", "what does a hospital", "what do hospitals",
        "how to treat", "how do you treat", "how to cure", "can i take", "should i take",
        "side effect", "dose of", "dosage",
        "how does referral", "how do referrals", "need a referral",
    )
    if any(pattern in lowered for pattern in clinical_query_patterns):
        return False

    kind = asked_kind(lowered)
    if kind:
        return True

    return any(word in lowered for word in NEARBY_WORDS) and bool(resolve_places(text))


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def _title(value: Any) -> str:
    """An official name as it should be shown to the patient reading the answer.

    The hierarchy carries some sectors and cells in block capitals, which is fine
    data and poor prose.
    """
    return " ".join(word.capitalize() for word in str(value or "").split())


# A word as a patient types it, accents and internal apostrophes included.
_WORD = re.compile(r"[\w']+", re.UNICODE)


def asks_for_nearby(text: str) -> bool:
    """True when the answer depends on where the patient is standing."""
    lowered = _norm(text)
    return any(word in lowered for word in NEARBY_WORDS) or bool(_RW_WHERE_PATTERNS.search(lowered))


@dataclass
class ResolvedPlace:
    """One official unit named by the patient, plus the units above it.

    A row keeps its own name in `name` and its ancestors in the level fields, so
    `_sector` answers "which sector is this in?" for a village and for a sector.
    """

    level: str
    name: str
    province: str = ""
    district: str = ""
    sector: str = ""

    @property
    def _province(self) -> str:
        return self.name if self.level == "province" else self.province

    @property
    def _district(self) -> str:
        return self.name if self.level == "district" else self.district

    @property
    def _sector(self) -> str:
        return self.name if self.level == "sector" else self.sector

    def areas(self) -> List["Area"]:
        """The register filters that can answer for this place, tightest first.

        The register files a facility by sector, district and province and knows no
        cells or villages, so a village is searched as the sector holding it and a
        district as the province above it.
        """
        found = []
        if self.level in ("village", "cell", "sector") and self._sector:
            # The district is part of the filter when we know it: 37 sector names
            # are used twice in the country, and "Kigali" sector is not the city.
            in_sector = {"sector__iexact": self._sector}
            if self._district:
                in_sector["district__iexact"] = self._district
            found.append(Area(self, "sector", _title(self._sector), in_sector))
        if self._district:
            found.append(
                Area(self, "district", _title(self._district), {"district__iexact": self._district})
            )
        if self._province:
            register_name = PROVINCE_REGISTER_NAMES.get(self._province, self._province)
            found.append(Area(self, "province", register_name, {"province__iexact": register_name}))
        if found:
            for area in found:
                area.origin = found[0].filter
        return found


@dataclass
class Area:
    """An area the facility table can be filtered by, and the place it came from.

    `filter` is what gets searched once a place has been widened out; `origin` is
    the area the patient actually named, kept because it is the right centre point
    to order a widened list around.
    """

    place: ResolvedPlace
    field: str
    label: str
    filter: Dict[str, str]
    origin: Dict[str, str] = field(default_factory=dict)


def _place_rows(text: str) -> List[Dict[str, Any]]:
    """Hierarchy rows whose official name is one of the message's words.

    Every official Rwandan place name is a single word, so the message's own words
    find them through one indexed lookup instead of comparing 17,000 names against
    the text.
    """
    lowered = _norm(text)
    words = {word.strip("'") for word in _WORD.findall(lowered)}
    if not words:
        return []
    # A province is written with a prefix in Kinyarwanda ("intara y'amajyepfo") and
    # with an adjective in English ("Northern Province"), so those are matched
    # inside the words rather than as whole ones.
    keys = words | {
        PROVINCE_WORDS[alias].lower()
        for alias in PROVINCE_WORDS
        if alias in lowered
    }
    return list(
        AdminPlace.objects.filter(is_active=True, name_key__in=sorted(keys)).values(
            "level", "name", "code", "province", "district", "sector"
        )
    )


def _rows_for_one_name(rows: List[Dict[str, Any]], context_districts: set) -> List[Dict[str, Any]]:
    """Decide which of the units sharing one name the patient means.

    A name that is also a district's own name means the district: Rwandans answer
    "where are you" with the district, and "ibitaro bya Huye" wants the district's
    hospitals, not the village of that name in Rubavu. Otherwise, copies of the name
    inside a single district are one neighbourhood and all are kept; copies spread
    over the country are decided by what the facility register itself knows - the
    district with a facility of that name is the place people mean (Kibuye is
    Karongi's old name because Kibuye Referral Hospital stands there), and failing
    that the district with the most care in it.
    """
    if context_districts:
        narrowed = [row for row in rows if _norm(row["district"]) in context_districts]
        rows = narrowed or rows

    as_district = [row for row in rows if row["level"] == "district"]
    if as_district:
        return as_district

    districts = {_norm(row["district"]) for row in rows if row["district"]}
    if len(districts) <= 1:
        return rows

    word = _norm(rows[0]["name"])
    named_there = [
        row
        for row in rows
        if HealthFacility.objects.filter(
            name__icontains=word, district__iexact=row["district"]
        ).exists()
    ]
    if named_there:
        return named_there
    busiest = max(
        districts,
        key=lambda district: HealthFacility.objects.filter(
            is_active=True, district__iexact=district
        ).count(),
    )
    return [row for row in rows if _norm(row["district"]) == busiest]


def resolve_places(text: str) -> List[ResolvedPlace]:
    """The places named in a message, resolved to the units the patient means.

    "Huye" is a district, a sector, a cell and several villages, and "Nyabugogo" is
    two cells and a village; the hierarchy holds every one of them, so which is
    meant is decided per name rather than by taking whichever row the database
    returned first.
    """
    rows = _place_rows(text)
    if not rows:
        return []
    # "Kigali" is both the city and a small sector in Nyarugenge. Writing a
    # province's name means the province, or a question about the whole city would
    # be answered with the two pharmacies on one hill in the centre.
    provinces_named = {_norm(row["name"]) for row in rows if row["level"] == "province"}
    if provinces_named:
        wider = [
            row for row in rows if row["level"] == "province" or _norm(row["name"]) not in provinces_named
        ]
        rows = wider or rows

    by_name: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        by_name.setdefault(_norm(row["name"]), []).append(row)
    named_districts = {_norm(row["name"]) for row in rows if row["level"] == "district"}

    chosen: List[Dict[str, Any]] = []
    for name_rows in by_name.values():
        district_context = (
            named_districts & {_norm(row["district"]) for row in name_rows}
            if len(by_name) > 1
            else set()
        )
        chosen += _rows_for_one_name(name_rows, district_context)

    seen, places = set(), []
    for row in chosen:
        if (row["level"], row["code"]) in seen:
            continue
        seen.add((row["level"], row["code"]))
        places.append(
            ResolvedPlace(
                level=row["level"],
                name=row["name"],
                province=row["province"],
                district=row["district"],
                sector=row["sector"],
            )
        )
    return places


def _usable_area(place: ResolvedPlace) -> Optional[Area]:
    """The tightest area around a place that can actually fill a short list.

    One or two rows may be all a sector truly has, and that is still the honest
    answer; an area with nothing mapped in it is not, so it widens to the district
    and then the province rather than telling the patient the country has no care
    where they are standing.
    """
    areas = place.areas()
    if not areas:
        return None
    counts = [(area, HealthFacility.objects.filter(is_active=True, **area.filter).count()) for area in areas]
    for area, count in counts:
        if count >= MIN_FACILITIES_FOR_AN_AREA:
            return area
    for area, count in counts:
        if count:
            return area
    return areas[0]


def _areas_for(text: str) -> List[Area]:
    """Every area to search for a message, de-duplicated across its place names."""
    areas = []
    for place in resolve_places(text):
        area = _usable_area(place)
        if area and area.filter not in [searched.filter for searched in areas]:
            areas.append(area)
    return areas


def distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    haversine = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))


def _centroid(facilities) -> Optional[Tuple[float, float]]:
    """The middle of a set of places, from the coordinates the surveyor recorded."""
    points = [
        (float(facility.latitude), float(facility.longitude))
        for facility in facilities
        if facility.latitude is not None and facility.longitude is not None
    ]
    if not points:
        return None
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def _maps_url(facility: HealthFacility) -> str:
    query = (
        f"{facility.latitude},{facility.longitude}"
        if facility.latitude is not None
        else facility.name
    )
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def _row(facility: HealthFacility, distance: Optional[float]) -> Dict[str, Any]:
    return {
        "name": facility.name,
        "type": facility.facility_type,
        "type_display": facility.get_facility_type_display(),
        "district": facility.district,
        "sector": facility.sector,
        "province": facility.province,
        "latitude": float(facility.latitude) if facility.latitude is not None else None,
        "longitude": float(facility.longitude) if facility.longitude is not None else None,
        "distance_km": round(distance, 1) if distance is not None else None,
        "maps_url": _maps_url(facility),
    }


def _dedupe(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """The dataset holds the same building two or three times under OSM ids.

    "2050 Pharmacy", "2050PHARMACY" and "2050 Pharmacy Ltd" are one place: spacing,
    punctuation and a corporate suffix are not a second pharmacy to send a patient to.
    """
    seen = set()
    unique = []
    for row in rows:
        name = re.sub(r"[^a-z0-9]", "", _norm(row["name"]))
        name = re.sub(r"(ltd|ltda|limited|sarl|sarlu|sa)$", "", name)
        key = (name, _norm(row["district"]))
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def search(
    text: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    limit: int = 6,
) -> FacilitySearch:
    """Rank facilities for a free-text question, by distance when we have one."""
    found = FacilitySearch(kind=asked_kind(text))
    areas = _areas_for(text)
    if areas:
        labels = list(dict.fromkeys(area.label for area in areas))
        levels = list(dict.fromkeys(area.field for area in areas))
        found.place = ", ".join(labels)
        found.place_level = levels[0] if len(levels) == 1 else None
        # Only worth quoting back when the search had to widen past the level the
        # patient used: their own word is the useful heading, the area is the
        # disclaimer beside it.
        narrower = [
            _title(area.place.name)
            for area in areas
            if LEVEL_TIGHTNESS[area.place.level] < LEVEL_TIGHTNESS[area.field]
        ]
        if narrower:
            found.locality = ", ".join(dict.fromkeys(narrower))
    if latitude is not None and longitude is not None:
        found.coordinates = (float(latitude), float(longitude))

    if not found.anchored:
        return found

    queryset = HealthFacility.objects.filter(is_active=True)
    if areas:
        area_filter = Q()
        for area in areas:
            area_filter |= Q(**area.filter)
        queryset = queryset.filter(area_filter)
    candidates = [
        facility for facility in queryset if not NOT_A_FACILITY.search(facility.name)
    ]

    if found.coordinates:
        lat0, lng0 = found.coordinates
        pairs = []
        for facility in candidates:
            if facility.latitude is None or facility.longitude is None:
                continue
            pairs.append(
                (
                    distance_km(lat0, lng0, float(facility.latitude), float(facility.longitude)),
                    facility,
                )
            )
        pairs.sort(key=lambda pair: pair[0])
        ranked = [_row(facility, distance) for distance, facility in pairs]
    else:
        # Named places sort by what the patient asked for and then by name, because
        # distance without coordinates would be a guess. A name that reads as a
        # facility comes first: this dataset holds "casa" and "EDF" as hospitals.
        #
        # Named places sort by what the patient asked for and then by distance from
        # the middle of the place named, because distance without coordinates would
        # otherwise be a guess: "hafi ya Nyabugogo" must not lead with a health
        # centre on the far side of the district. The centre is the mean of the
        # register's own rows, so it is where the facilities are rather than a
        # coordinate invented for a neighbourhood, and it only ever orders the list
        # - it is never printed as a distance.
        # A search that had to widen past the place named keeps its centre on the
        # rows that place does have, so the list still starts beside the patient.
        widened = [area for area in areas if area.origin != area.filter]
        anchor = None
        if widened:
            origins = Q()
            for area in widened:
                origins |= Q(**area.origin)
            anchor = _centroid(HealthFacility.objects.filter(is_active=True).filter(origins))
        anchor = anchor or _centroid(candidates)

        def away_from_centre(facility: HealthFacility) -> float:
            if anchor is None or facility.latitude is None or facility.longitude is None:
                return float("inf")
            return distance_km(
                anchor[0], anchor[1], float(facility.latitude), float(facility.longitude)
            )

        ordered = sorted(
            candidates,
            key=lambda f: (
                0 if FACILITY_IN_NAME.search(f.name) else 1,
                TYPE_PRIORITY.get(f.facility_type, 9),
                round(away_from_centre(f), 1),
                _norm(f.name),
            ),
        )
        ranked = [_row(facility, None) for facility in ordered]

    ranked = _dedupe(ranked)
    if found.kind:
        same_kind = [row for row in ranked if row["type"] == found.kind]
        # A district often has more rows tagged hospital than actually are: prefer
        # the ones a patient would recognise by name, and fall back rather than
        # return nothing.
        named = [row for row in same_kind if FACILITY_IN_NAME.search(row["name"])]
        found.results = (named or same_kind or ranked)[:limit]
    else:
        found.results = ranked[:limit]
    return found
