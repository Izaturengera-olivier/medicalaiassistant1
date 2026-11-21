"""What a facility question is asking, and which facility it names.

"Which sector is Rwankeri Health Center in?" is one question about one place.
"Health centres near Rwankeri" is a different question about an area. Answering
the first with the second is not a rough answer: it is an answer to a question
the patient did not ask, which reads as the assistant not listening.

The classifier works from wording alone, so a symptom message never reads the
register. When the wording does name one facility, the resolver matches it
against verified rows and the caller answers that fact directly instead of
letting a model guess.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from knowledge.models import HealthFacility
from knowledge.services.facility_service import asked_kind, asks_for_nearby

INTENT_NEARBY = "nearby_facilities"
INTENT_LOCATION = "location_lookup"
INTENT_SECTOR = "administrative_sector_lookup"
INTENT_DISTRICT = "administrative_district_lookup"
INTENT_PROVINCE = "administrative_province_lookup"
INTENT_SERVICES = "services_lookup"
INTENT_DIRECTIONS = "directions"
INTENT_EXPLANATION = "entity_explanation"

ENTITY_INTENTS = (
    INTENT_LOCATION,
    INTENT_SECTOR,
    INTENT_DISTRICT,
    INTENT_PROVINCE,
    INTENT_SERVICES,
    INTENT_DIRECTIONS,
    INTENT_EXPLANATION,
)

# The register column each administrative intent asks for.
ADMIN_FIELDS = {
    INTENT_SECTOR: "sector",
    INTENT_DISTRICT: "district",
    INTENT_PROVINCE: "province",
}

# "District Hospital" is a facility name, not a request for the district column.
# Kinyarwanda drops the noun-class vowel after locative "mu"/"ku": the same word
# is "umurenge" alone but "mu murenge" in a sentence, "intara" but "mu ntara".
_FIELD_PATTERNS = (
    (INTENT_SECTOR, re.compile(r"\b(?:sector|secteur|u?murenge|imirenge|mirenge)\b", re.I)),
    (
        INTENT_DISTRICT,
        re.compile(r"\b(?:district|akarere|uturere|karere)\b(?!\s+(?:hospital|health))", re.I),
    ),
    (INTENT_PROVINCE, re.compile(r"\b(?:province|intara|ntara)\b", re.I)),
    (INTENT_SERVICES, re.compile(r"\b(?:services?|serivisi|prestations?)\b", re.I)),
)

_DIRECTIONS = re.compile(
    r"(?:how (?:do|can|should) i (?:get|reach|go) to|directions? to|route to|"
    r"inzira (?:igana|yaho)|nzabona nte|comment (?:aller|me rendre|y aller)|"
    r"itin[ée]raire|se rendre)",
    re.I,
)

_LOCATION = re.compile(
    r"(?:where(?:'s| is) (?:the )?|where can i find|iherereye|iherereye he|"
    r"iri he|irihe|ni hehe|se trouve|où se trouve|ou se trouve|localisation|"
    r"localis[ée]|situ[ée])",
    re.I,
)

_EXPLANATION = re.compile(
    r"(?:what (?:is|are)|what's|tell me about|explain|describe|ni iki|"
    r"qu'est-ce que|qu est ce que|pr[ée]sentez|d[ée]cri(?:re|vez))",
    re.I,
)

# A patient telling the assistant it answered something else. The corrected
# question is answered from the facility they named, not from the last reply.
_CORRECTION = re.compile(
    r"(?:not what i (?:asked|wanted)|that(?:'s| is) not what|"
    r"no,? (?:that|i (?:want|asked|meant))|i (?:did not|didn't) ask|"
    r"si (?:icyo|ibyo) nabajije|ntibyo nabajije|nticyo nabajije|"
    r"ce n'est pas ce que j'ai demand|je n'ai pas demand)",
    re.I,
)

# Facility type wording, used to find the name around it. The name is the words
# in front ("Rwankeri Health Center") or, in French, after ("le centre de santé
# de Rwankeri").
_TYPE_RE = re.compile(
    r"(health\s+(?:center|centre|post)s?|hospitals?|clinics?|pharmac(?:y|ies)|"
    r"centres?\s+de\s+sant[ée]s?|centres?\s+hospitaliers?|"
    r"h[ôo]pitals?|cliniques?|pharmacies?|dispensaires?|"
    r"ivuriro|ibitaro|kliniki|farumasi)",
    re.I,
)

# The type comes first in these phrases, so the name follows it.
_TYPE_FIRST_RE = re.compile(
    r"^(?:centres?\s+de\s+sant[ée]s?|centres?\s+hospitaliers?|h[ôo]pitals?|"
    r"cliniques?|pharmacies?|dispensaires?)",
    re.I,
)

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9'’‑-]+")
_AFTER_CONNECTORS = {"de", "du", "des", "d", "la", "le", "les", "l", "au", "aux", "a", "à"}
# A locative word in front of the type word introduces a place, not a name:
# "health centre in Gakenke" is about Gakenke. "Of"/"de" are excluded because
# "the sector of Rwankeri Health Center" still names the facility.
_NAME_BREAKERS = {
    "in", "at", "near", "around",
    "i", "muri", "ku", "hafi", "dans", "au", "aux", "a", "à", "pres", "près", "proche",
}
# Words that introduce a facility's name. After one of them the name may be
# written in lower case ("the sector of rwankeri health centre"); without one,
# the word in front of the type is a name only if it reads as a proper noun,
# which is what keeps "I have fever, which health center…" out of this path.
_NAME_CONNECTORS = {"of", "de", "du", "des", "ya", "wa", "rya", "cya", "bya"}

# Words that never distinguish one facility name from another. Type words are
# here on purpose: "health center" is what a patient calls the place, not the name.
_STOPWORDS = {
    # English grammar and question wording
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "am",
    "do", "does", "did", "can", "could", "should", "would", "will", "shall",
    "may", "might", "must", "i", "we", "you", "he", "she", "it", "they", "me",
    "us", "my", "our", "your", "his", "her", "their", "its", "this", "that",
    "these", "those", "there", "here", "where", "when", "why", "what", "which",
    "who", "whom", "how", "not", "no", "yes", "so", "if", "then", "than",
    "and", "or", "but", "of", "in", "on", "at", "to", "for", "from", "with",
    "by", "about", "into", "over", "under", "near", "nearest", "nearby",
    "close", "closest", "around", "please", "tell", "show", "give", "want",
    "wanted", "need", "know", "help", "asked", "ask", "says", "said", "locate",
    "located", "location", "address", "find", "get", "go", "reach", "take",
    "see", "use", "using", "exactly", "just", "only", "also", "too", "very",
    "much", "many", "more", "most", "some", "any", "all", "both", "each",
    "list", "give", "tell", "named", "called", "called", "please",
    # Facility type words
    "hospital", "hospitals", "health", "center", "centre", "centers", "centres",
    "post", "posts", "clinic", "clinics", "pharmacy", "pharmacies", "dispensary",
    "dispensaire", "dispensaires", "ivuriro", "ibitaro", "kliniki", "farumasi",
    "hopital", "hopitaux", "clinique", "pharmacie", "hospitalier", "hospitaliere",
    # Administrative field words
    "sector", "secteur", "murenge", "umurenge", "imirenge", "district", "akarere",
    "karere", "uturere", "province", "intara", "ntara",
    "service", "services", "serivisi", "prestation", "prestations",
    # French grammar
    "le", "la", "les", "l", "un", "une", "des", "du", "de", "d", "au", "aux",
    "a", "à", "et", "ou", "où", "est", "sont", "etre", "ête", "dans", "sur",
    "sous", "avec", "sans", "pour", "par", "pas", "ne", "plus", "très", "tres",
    "que", "qui", "quoi", "quel", "quelle", "quels", "quelles", "comment",
    "pourquoi", "quand", "combien", "se", "sa", "son", "ses", "ce", "cette",
    "ces", "je", "j", "tu", "il", "elle", "nous", "vous", "ils", "elles",
    "mon", "ma", "mes", "votre", "vos", "notre", "nos", "leur", "leurs", "y",
    "en", "s", "c", "n", "qu", "trouve", "trouver", "situe", "situer",
    "localise", "localiser", "donne", "donner", "dire", "savoir", "connaitre",
    "besoin", "veux", "voudrais", "cherche", "sante", "médecin", "medecin",
    "adresse", "itineraire", "itinéraire", "bonjour", "merci", "s'il", "vous",
    "offre", "offrent", "propose", "proposent", "fournit", "fournissent",
    "aller", "vais", "rendre", "vers", "arriver", "depuis",
    # Kinyarwanda grammar and question wording
    "ni", "mu", "ku", "kwa", "kuri", "wa", "ya", "rya", "cya", "bya", "za",
    "he", "hehe", "irihe", "iri", "riri", "kiri", "biri", "irimo", "iyihe",
    "izihe", "uwuhe", "uwu", "uyu",
    "aho", "aha", "ndi", "uri", "ari", "turi", "kandi", "cyangwa", "ariko",
    "nka", "nta", "ntacyo", "icyo", "ibyo", "iki", "ese", "yego", "oya",
    "mbwira", "mbwire", "mfasha", "nshaka", "ndashaka", "iherereye",
    "giherereye", "kiherereye", "hafi", "ubuvuzi", "ubuzima", "umuganga",
    "muganga", "rwanda", "rwandan", "country", "national",
}

MAX_ENTITY_CANDIDATES = 5


@dataclass(frozen=True)
class FacilityQuestion:
    """The intent read from the patient's wording, before any data is read."""

    intent: str
    kind: Optional[str] = None
    correction: bool = False

    @property
    def entity_intent(self) -> bool:
        return self.intent in ENTITY_INTENTS

    @property
    def admin_field(self) -> Optional[str]:
        return ADMIN_FIELDS.get(self.intent)


@dataclass
class EntityLookup:
    """The facilities whose names match the one the patient used."""

    facilities: List[HealthFacility]
    asked_name: str
    asked_kind: Optional[str] = None


def _asked_field(text: str) -> Optional[str]:
    for intent, pattern in _FIELD_PATTERNS:
        if pattern.search(text or ""):
            return intent
    return None


def classify(text: str) -> Optional[FacilityQuestion]:
    """The facility intent in a message, or None when it is not one.

    Only wording that names a facility type, asks for a kind near a place, or
    corrects an earlier facility answer gets here: a symptom message stays out.
    """
    if not (text or "").strip():
        return None
    kind = asked_kind(text)
    nearby = asks_for_nearby(text)
    field = _asked_field(text)
    correction = bool(_CORRECTION.search(text))
    # A field word plus a facility type is only a question about one facility
    # when the message also names one. "I have fever, which health center in this
    # district?" asks for a list, and belongs to the nearby path.
    name, _ = entity_name(text)
    if not name and kind and not correction:
        # Names typed in lower case have no capital to mark them, so the register
        # decides whether the word in front of the type is a facility.
        name = registered_lowercase_name(text)

    if field and (correction or (kind and name)):
        return FacilityQuestion(intent=field, kind=kind, correction=correction)
    # A list near a place is a list, even when the sentence also says "where".
    if nearby and kind:
        return FacilityQuestion(intent=INTENT_NEARBY, kind=kind)
    # "Where is the health center in Gakenke?" names a place, not a facility:
    # with no name there is no single row to answer about, so it stays a list.
    if _DIRECTIONS.search(text) and kind and name:
        return FacilityQuestion(intent=INTENT_DIRECTIONS, kind=kind, correction=correction)
    if _LOCATION.search(text) and kind and name:
        return FacilityQuestion(intent=INTENT_LOCATION, kind=kind, correction=correction)
    if _EXPLANATION.search(text) and kind and name:
        return FacilityQuestion(intent=INTENT_EXPLANATION, kind=kind, correction=correction)
    return None


def _normalise(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-z0-9 ]+", " ", value.lower())
    return " ".join(value.split())


def _is_stopword(token: str) -> bool:
    """Whether a normalised token is grammar, including apostrophe phrases.

    ``_normalise`` splits "Qu'est-ce" into "qu est ce", so the whole token never
    matches the stopword list even though each of its parts does. Reading such a
    phrase as a name turned "Qu'est-ce que le centre de santé …" into a lookup
    for a facility called "Qu'est-ce".
    """
    if token in _STOPWORDS:
        return True
    parts = [part for part in token.split() if part]
    return len(parts) > 1 and all(part in _STOPWORDS for part in parts)


def _distinctive_tokens(text: str) -> List[str]:
    tokens = []
    for word in _WORD_RE.findall(text or ""):
        token = _normalise(word).strip("-")
        if len(token) < 2 or _is_stopword(token):
            continue
        tokens.append(token)
    return list(dict.fromkeys(tokens))


def _name_before(text: str, start: int) -> str:
    """The name the words in front of the type word spell, if any.

    "Rwankeri Health Center" is a name; "health center in Gakenke" is a place, so
    a name that is introduced by a locative word is discarded rather than turned
    into a facility lookup for the district.
    """
    collected = []
    for word in reversed(_WORD_RE.findall(text[:start])):
        token = _normalise(word).strip("-")
        if _is_stopword(token) or len(token) < 2:
            if collected:
                if token in _NAME_BREAKERS:
                    return ""
                if token in _NAME_CONNECTORS or any(word[:1].isupper() for word in collected):
                    return " ".join(reversed(collected))
                # "I have fever, which health center should I go to?" collects a
                # symptom word, not a name: leave it to the nearby list instead.
                return ""
            continue
        # A lower-case word in front of an already collected name is the rest of
        # the sentence ("… irimo Rwankeri Hospital"), so the name ends there.
        if collected and not word[:1].isupper():
            break
        collected.append(word)
        if len(collected) >= 4:
            break
    if collected and not any(word[:1].isupper() for word in collected):
        return ""
    return " ".join(reversed(collected))


def _name_after(text: str, end: int) -> str:
    """The name after a French type-first phrase ("centre de santé de X")."""
    collected = []
    for word in _WORD_RE.findall(text[end:]):
        token = _normalise(word).strip("-")
        if token in _AFTER_CONNECTORS:
            if collected:
                break
            continue
        if _is_stopword(token) or len(token) < 2:
            break
        collected.append(word)
        if len(collected) >= 3:
            break
    return " ".join(collected)


def _loose_name_before(text: str, start: int) -> str:
    """The words in front of the type word with no capital marking a name.

    Patients often type names in lower case ("where rwankeri health center
    located?"), so the capital check that keeps "I have fever, which health
    center…" out cannot be used here. The caller confirms the candidate against
    the register instead.
    """
    collected = []
    for word in reversed(_WORD_RE.findall(text[:start])):
        token = _normalise(word).strip("-")
        if _is_stopword(token) or len(token) < 2:
            if collected:
                if token in _NAME_BREAKERS or token in _NAME_CONNECTORS:
                    return ""
                return " ".join(reversed(collected))
            continue
        collected.append(word)
        if len(collected) >= 3:
            break
    return " ".join(reversed(collected))


def registered_lowercase_name(text: str) -> str:
    """A lower-case name candidate that the register itself confirms.

    Without a capital, a word in front of the type is treated as a facility name
    only when a register row starts with it. That answers "where rwankeri health
    center located?" without turning "I have fever, which health center…" into a
    lookup for a facility called "fever".
    """
    for match in _TYPE_RE.finditer(text or ""):
        candidate = _loose_name_before(text, match.start())
        if not candidate:
            continue
        tokens = _distinctive_tokens(candidate)
        if not tokens:
            continue
        rows = _matching_rows(tokens)
        if any(
            _normalise(facility.name).startswith(tokens[0])
            for _, facility in rows.values()
        ):
            return candidate
    return ""


# The name comes after the destination preposition of a directions question.
# "Comment aller à Rwankeri" cannot use the words in front of the type word,
# because the preposition itself is one of the locatives that discard a name.
_DIRECTION_NAME = re.compile(
    r"(?:(?:how (?:do|can|should) i (?:get|reach|go)|directions?|route|"
    r"comment (?:aller|me rendre|y aller)|itin[ée]raire|se rendre|"
    r"inzira (?:igana|yaho)|nzabona nte)\b[^,.;?]*?"
    r"\b(?:to|a|à|au|aux|kwa|kuri|vers)\s+)(.+)",
    re.I,
)


def _direction_name(text: str) -> str:
    match = _DIRECTION_NAME.search(text or "")
    if not match:
        return ""
    collected = []
    for word in _WORD_RE.findall(match.group(1)):
        token = _normalise(word).strip("-")
        if not word[:1].isupper() or _is_stopword(token) or len(token) < 2:
            break
        collected.append(word)
        if len(collected) >= 4:
            break
    return " ".join(collected)


def entity_name(text: str, typed_only: bool = False) -> Tuple[str, bool]:
    """The facility name in the wording, and whether it must start the row name.

    French names come after the type phrase, so they are searched from the start
    of the row name: that rejects "Pharmacy, Gakenke" when the patient typed
    "le centre de santé de Gakenke" and means a health centre there.

    ``typed_only`` drops the last-resort reading of every remaining word as a
    name. A correction sentence ("No, that is not what I asked") is mostly
    grammar, and one of its words can prefix a facility name by accident.
    """
    value = text or ""
    for match in _TYPE_RE.finditer(value):
        name = _name_before(value, match.start())
        if name:
            return name, False
    for match in _TYPE_RE.finditer(value):
        if not _TYPE_FIRST_RE.match(match.group(0)):
            continue
        name = _name_after(value, match.end())
        if name:
            return name, True
    if not typed_only:
        name = _direction_name(value)
        if name:
            return name, True
    if typed_only:
        return "", False
    if not _TYPE_RE.search(value):
        # "Where is Rwankeri located?" never says the type; the remaining words
        # are the name, and it has to start the row so a district name is not
        # matched to a pharmacy that merely mentions it.
        tokens = _distinctive_tokens(value)
        if tokens:
            return " ".join(tokens), True
    return "", False


def _matching_rows(tokens: Sequence[str]) -> Dict[int, Tuple[int, HealthFacility]]:
    found: Dict[int, Tuple[int, HealthFacility]] = {}
    for token in sorted(set(tokens), key=len, reverse=True):
        if len(token) < 3:
            continue
        rows = HealthFacility.objects.filter(
            is_active=True, name__icontains=token
        )[:200]
        for facility in rows:
            name = _normalise(facility.name)
            hits = sum(1 for candidate in tokens if candidate in name)
            if not hits:
                continue
            previous = found.get(facility.pk)
            if previous is None or hits > previous[0]:
                found[facility.pk] = (hits, facility)
    return found


def _dedupe(facilities: Sequence[HealthFacility]) -> List[HealthFacility]:
    seen = set()
    unique = []
    for facility in facilities:
        key = (_normalise(facility.name), _normalise(facility.sector), _normalise(facility.district))
        if key in seen:
            continue
        seen.add(key)
        unique.append(facility)
    return unique


def resolve_entity(
    text: str, kind: Optional[str] = None, typed_only: bool = False
) -> Optional[EntityLookup]:
    """The register rows the message's facility name matches.

    A single row is the answer even when its type differs from the patient's
    wording ("Rwankeri Health Center" against the register's Rwankeri Hospital);
    the caller says so instead of pretending the register has a health centre.
    When several rows share the name, the asked type breaks the tie, and a tie
    that still cannot be broken is returned so the reply can show each sector.
    """
    name, strict = entity_name(text, typed_only=typed_only)
    if not name and not typed_only:
        name = registered_lowercase_name(text)
        strict = True
    tokens = _distinctive_tokens(name)
    if not tokens:
        return None

    rows = _matching_rows(tokens)
    if not rows:
        return None
    best = max(hits for hits, _ in rows.values())
    pool = [facility for hits, facility in rows.values() if hits == best]

    if strict:
        pool = [facility for facility in pool if _normalise(facility.name).startswith(tokens[0])]
        if not pool:
            return None

    if kind:
        typed = [facility for facility in pool if facility.facility_type == kind]
        if typed:
            pool = typed
        elif len(pool) > 1:
            # Several rows match the words but none is the type the patient
            # named: that is not a facility name we can verify.
            return None

    pool.sort(
        key=lambda facility: (
            _normalise(facility.name) != _normalise(name),
            len(facility.name),
            facility.name.lower(),
        )
    )
    pool = _dedupe(pool)[:MAX_ENTITY_CANDIDATES]
    return EntityLookup(facilities=pool, asked_name=name.strip(), asked_kind=kind)


def resolve_entity_from_history(history: Optional[Sequence[dict]]) -> Optional[EntityLookup]:
    """The last facility the patient named, for "no, I meant the sector" turns."""
    for turn in reversed(list(history or [])):
        if turn.get("role") != "user":
            continue
        content = turn.get("content") or ""
        if not asked_kind(content):
            continue
        lookup = resolve_entity(content)
        if lookup is not None:
            return lookup
    return None


def display_name(text: str) -> str:
    """The name as the patient wrote it, for a reply that could not verify it."""
    name, _ = entity_name(text)
    if name:
        return name
    return " ".join(word.title() for word in _distinctive_tokens(text))


def validate_entity_answer(
    reply: str,
    question: FacilityQuestion,
    facilities: Sequence[HealthFacility],
    accepted_values: Sequence[str] = (),
) -> bool:
    """Whether the reply names the facility and carries the requested fact.

    A field the register leaves empty is a valid answer only when the reply says
    it is not recorded; a missing fact must never be silently replaced.

    ``accepted_values`` carries facts the caller states in translation: a
    Kinyarwanda answer names a province as "mu ntara y'Iburengerazuba", so the
    column's own "Western Province" never appears in the reply.
    """
    text = _normalise(reply)
    if not text:
        return False
    if not any(_normalise(facility.name) in text for facility in facilities):
        return False

    if question.intent in ADMIN_FIELDS:
        field = ADMIN_FIELDS[question.intent]
        values = [
            _normalise(getattr(facility, field))
            for facility in facilities
            if getattr(facility, field)
        ] + [_normalise(value) for value in accepted_values if value]
        if values and any(value in text for value in values):
            return True
        return any(
            phrase in text
            for phrase in (
                "not record", "does not record", "nticyandika", "ntibwandika",
                "n indique pas", "ne precise pas",
            )
        )
    return True
