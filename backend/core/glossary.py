"""Kinyarwanda medical terminology shared by retrieval and prompt building.

Approved sources publish in English, so a Kinyarwanda question has to carry its
English equivalents before it can match anything. The same map keeps the model's
Kinyarwanda terminology consistent when it answers.
"""

from typing import Dict, List, Set, Tuple
import re

# Kinyarwanda term -> English search terms. Keys are matched as substrings
# because Kinyarwanda is agglutinative ("ndababara mu nda" carries no bare
# word "inda"), so every key must be at least MIN_TERM_LENGTH characters.
#
# A few roots are exceptions: "inda" (belly) is also the tail of the verb stems
# "-rinda" (protect/prevent), "-shinda" (succeed) and "-gwinda", so substring
# matching turned "nshaka amakuru ku ndwara ya ebola nuko wayirinda" (how to
# prevent Ebola) into an abdominal-pain query. Those keys need WHOLE_WORD_TERMS.
MEDICAL_TERMS: Dict[str, str] = {
    # Symptoms & Pain
    "umuriro": "fever pyrexia temperature",
    "ubushyuhe": "fever temperature pyrexia",
    "inkorora": "cough coughing respiratory",
    "ibicurane": "common cold flu influenza nasal congestion",
    "umutwe": "headache head pain migraine",
    "inda": "abdominal pain stomach pain gastralgia",
    "mu nda": "abdominal pain stomach pain cramps",
    "igifu": "stomach gastritis ulcer abdominal pain",
    "babara": "pain discomfort ache",
    "ububabare": "pain discomfort ache",
    "uburibwe": "pain discomfort ache",
    "umugongo": "back pain lumbar spine",
    "mu gituza": "chest pain chest discomfort angina",
    "gituza": "chest pain chest discomfort thorax",
    "gatuza": "chest pain chest discomfort thorax",
    "muhogo": "sore throat pharyngitis throat pain",
    "amenyo": "toothache dental pain teeth",
    "amatwi": "ear pain ear infection otitis",
    "amaso": "eye pain vision conjunctivitis",
    "amaguru": "leg pain swelling legs oedema",
    "amaboko": "arm pain arms numbness",
    "impiswi": "diarrhoea loose stools dysentery",
    "gucibwamo": "diarrhoea loose stools dysentery",
    "guhitwa": "constipation hard stools",
    "kuruka": "vomiting emesis nausea",
    "gusesema": "nausea feeling sick queasy",
    "isesemi": "nausea feeling sick queasy",
    "umunaniro": "fatigue tiredness exhaustion weakness",
    "naniwe": "fatigue tiredness exhaustion weakness",
    "kuruha": "fatigue tiredness exhaustion",
    "guhumeka": "breathing shortness of breath dyspnea respiratory",
    "umwuka": "breath shortness of breath dyspnea difficulty breathing",
    "ibyuya": "sweating night sweats perspiration",
    "gutitira": "chills shivering rigors",
    "kubyimba": "swelling oedema inflammation puffiness",
    "ibiheri": "rash skin eruption hives eczema",
    "kuvirirana": "bleeding haemorrhage hemorrhage",
    "amaraso": "blood bleeding anaemia hematology",
    "kuzungerwa": "dizziness lightheadedness vertigo",
    "gucika intege": "weakness lethargy fatigue",
    "kwibagirwa": "memory loss confusion dementia",
    "ibingibingi": "dizziness vertigo",
    "ikizunguzungu": "dizziness vertigo lightheadedness",
    "kubura umwuka": "shortness of breath respiratory distress dyspnea",
    "uruhu": "skin dermatology rash itching",
    "kuryaryata": "itching pruritus tingling",
    "kubabara mu ngingo": "joint pain arthritis arthralgia",
    "ingingo": "joints articulation musculoskeletal",
    "kugwa igihumure": "syncope fainting loss of consciousness",
    "guta ubwenge": "loss of consciousness altered mental status coma",
    "kubura ibitotsi": "insomnia sleep disorder sleeplessness",
    "kuribwa mu rurimi": "tongue pain oral ulcer stomatitis",
    "kuribwa mu nda": "abdominal pain stomach ache cramps",

    # Conditions & Pathologies
    "malariya": "malaria plasmodium fever",
    "diabeti": "diabetes blood sugar hyperglycemia",
    "diyabete": "diabetes blood sugar hyperglycemia",
    "isukari": "diabetes blood sugar glucose",
    "umuvuduko": "blood pressure hypertension cardiovascular",
    "umuvuduko w'amaraso": "high blood pressure hypertension cardiovascular",
    "umusonga": "pneumonia tuberculosis respiratory infection",
    "asima": "asthma wheezing inhaler bronchospasm",
    "kanseri": "cancer oncology tumor neoplasm",
    "sida": "HIV AIDS immunocompromised",
    "indwara y'umutima": "heart disease cardiac heart failure",
    "ndwara": "disease illness condition disorder pathology",
    "umutima": "heart cardiac cardiovascular",
    "impyiko": "kidney renal nephrology",
    "umwijima": "liver hepatic hepatitis",
    "igituntu": "tuberculosis TB respiratory",
    "imbwa": "epilepsy seizure convulsions",
    "igicuri": "epilepsy seizure convulsions",
    "guturika k'umutwe": "stroke cerebrovascular accident apoplexy",
    "kugagara": "spasm stiffness tetany rigidity",
    "ijosi rikomeye": "stiff neck meningitis emergency",
    "kurwara mu muhogo": "pharyngitis strep throat tonsillitis",
    "inzoka": "worms helminths intestinal parasites",

    # Care and clinical vocabulary
    "imiti": "medicine drugs medication prescription pharmaceutical",
    "umuti": "medicine drug medication prescription",
    "urukingo": "vaccine vaccination immunization",
    "inkingo": "vaccines immunizations schedule",
    "isuzuma": "examination assessment diagnosis screening",
    "gusuzuma": "examine assess diagnose screen",
    "ibimenyetso": "symptoms signs manifestations indicators",
    "ikimenyetso": "symptom sign manifestation indicator",
    "umuganga": "doctor clinician physician medical officer",
    "abagangakazi": "nurses healthcare workers clinicians",
    "umuforomo": "nurse caregiver medical assistant",
    "abaforomo": "nurses nursing healthcare team",
    "farumasi": "pharmacy pharmacist medication drug store",
    "ibitaro": "hospital medical center inpatient",
    "ivuriro": "health centre clinic outpatient healthcare facility",
    "gutwita": "pregnancy pregnant maternal gestation",
    "kubyara": "childbirth delivery obstetrics labor",
    "umwana": "child infant paediatric pediatric newborn",
    "abana": "children pediatric health vaccination nutrition",
    "umubyeyi": "mother parent maternal",
    "ababyeyi": "maternal child health parents",
    "amaraso make": "anaemia anemia low hemoglobin",
    "akaga": "emergency warning signs danger crisis",
    "ubwihutirwe": "urgency emergency prompt review",
    "inyongera": "supplement follow-up vitamin",
    "ebola": "ebola viral haemorrhagic fever filovirus",
    "serwakira": "marburg viral haemorrhagic fever epidemic outbreak",
    "marburg": "marburg viral haemorrhagic fever epidemic outbreak",
    "kolera": "cholera severe watery diarrhoea dehydration",
    "iseme": "measles rash immunization fever",
    "kurinda": "prevention prevent protective measures",
    "yirinda": "prevention prevent protect yourself avoid",
    "gukingira": "prevention protect shield avoid",
    "kwirinda": "prevention hygiene precautions safety",
    "ubudahangarwa": "immunity immune system resistance",

    # Diagnostics & Tests
    "ibipimo": "tests diagnostic labs laboratory scan imaging",
    "gupima": "test check measure screen diagnose",
    "ibisubizo": "test results laboratory findings impression",
    "radiyografi": "X-ray radiography chest imaging",
    "ekografi": "ultrasound sonography echography",
    "echographie": "ultrasound sonography scan",
    "agapimo": "rapid test diagnostic check RDT",
    "gupima umuriro": "temperature measurement thermometer fever",
    "gupima amaraso": "blood test laboratory CBC CMP",
    "gupima inkari": "urinalysis urine test dipstick",

    # Rwanda Health System & Care Delivery
    "mituweli": "health insurance CBHI Mutuelle de Sante coverage",
    "mutuelle": "health insurance CBHI Mutuelle de Sante coverage",
    "abajyanama b'ubuzima": "community health workers primary care triage",
    "abajyanama": "community health workers primary care triage",
    "ubuvuzi": "healthcare medical care medical treatment",
    "kwivuza": "seek care medical treatment health facility",
    "kwivuriza": "seek care health facility clinic hospital",
    "kuvurwa": "receive care treatment medical attention",
    "urusobane": "referral transfer health system care level",
    "samu": "emergency medical ambulance SAMU 112 912",
    "isange": "isange one stop centre medical emergency GBV",
    "shisha kibondo": "nutrition child maternal supplement stunting",
    "gahunda y'inkingo": "immunization schedule vaccines vaccination EPI",
    "ibitaro bikuru": "referral teaching hospital CHUK CHUB RMH King Faisal",
    "ibitaro by'akarere": "district hospital inpatient surgical care",
    "ibitaro by'intara": "provincial referral hospital inpatient specialized",
    "amavuriro": "health centres clinics health posts outpatient",
    "poste de sante": "health post primary care cell level",
    "kigo nderabuzima": "health centre primary care health facility",
    "urupapuro rwo kohereza": "transfer sheet referral letter health system",
    "urupapuro": "transfer form referral document prescription",
    "ruhengeri": "Ruhengeri referral hospital Northern province",
    "chuk": "CHUK University Teaching Hospital of Kigali referral",
    "chub": "CHUB University Teaching Hospital of Butare referral",
    "king faisal": "King Faisal Hospital tertiary referral Kigali",
    "mmi": "Military Medical Insurance MMI healthcare",
    "rama": "RAMA RSSB health insurance public servants",
}

MIN_TERM_LENGTH = 4

# Keys that must appear as a standalone word, because as a substring they also
# occur inside unrelated verb stems (see MEDICAL_TERMS above).
WHOLE_WORD_TERMS = frozenset({"inda", "uruhu"})


def _term_pattern(term: str) -> re.Pattern:
    escaped = re.escape(term)
    if term in WHOLE_WORD_TERMS:
        return re.compile(f"(?<![a-z]){escaped}(?![a-z])")
    return re.compile(escaped)


_PATTERNS = {term: _term_pattern(term) for term in MEDICAL_TERMS}

# Key phrases indicating user wants the response specifically in Kinyarwanda
_KINYARWANDA_INTENT_PATTERNS = [
    re.compile(r"\b(?:in|into)\s+(?:kinyarwanda|ikinyarwanda)\b", re.IGNORECASE),
    re.compile(r"\b(?:subiza|andika|sobanura|vuga|koresha)\s+(?:mu\s+)?(?:k|ik)inyarwanda\b", re.IGNORECASE),
    re.compile(r"\bmu\s+(?:k|ik)inyarwanda\b", re.IGNORECASE),
    re.compile(r"\btranslate\s+(?:to|into)\s+(?:k|ik)inyarwanda\b", re.IGNORECASE),
    re.compile(r"\b(?:answer|explain|reply)\s+in\s+(?:k|ik)inyarwanda\b", re.IGNORECASE),
    re.compile(r"\bkinyarwanda\s+(?:please|nyamuneka)\b", re.IGNORECASE),
]

_ENGLISH_INTENT_PATTERNS = [
    re.compile(r"\b(?:in|into)\s+english\b", re.IGNORECASE),
    re.compile(r"\b(?:answer|explain|reply|translate)\s+(?:in|to|into)\s+english\b", re.IGNORECASE),
    re.compile(r"\bsubiza\s+mu\s+cyongereza\b", re.IGNORECASE),
    re.compile(r"\bmu\s+cyongereza\b", re.IGNORECASE),
]


def requests_kinyarwanda(text: str) -> bool:
    """True if the user's message specifically requests a response in Kinyarwanda."""
    if not text:
        return False
    return any(pattern.search(text) for pattern in _KINYARWANDA_INTENT_PATTERNS)


def requests_english(text: str) -> bool:
    """True if the user's message specifically requests a response in English."""
    if not text:
        return False
    return any(pattern.search(text) for pattern in _ENGLISH_INTENT_PATTERNS)


def matched_terms(text: str) -> List[str]:
    """Return the English search terms for Kinyarwanda terms present in text."""
    lowered = (text or "").lower()
    english: List[str] = []
    for kinyarwanda, terms in MEDICAL_TERMS.items():
        if len(kinyarwanda) < MIN_TERM_LENGTH:
            continue
        if _PATTERNS[kinyarwanda].search(lowered):
            english.append(terms)
    # Deduplicate while keeping order so repeated terms do not bloat the query.
    return list(dict.fromkeys(english))


def expand_query(text: str, max_length: int = 2000) -> str:
    """Append English equivalents of any Kinyarwanda terms found in text."""
    terms = matched_terms(text)
    if not terms:
        return text
    return f"{text} {' '.join(terms)}"[:max_length]


def glossary_compact() -> str:
    """Render the glossary as a single compact line for inclusion in a prompt."""
    return "; ".join(f"{rw}={en}" for rw, en in MEDICAL_TERMS.items())


# High-frequency patient vocabulary that stays in the prompt even when the
# message does not use it: the model needs these whichever symptom is discussed.
_CORE_GLOSSARY_TERMS = (
    "umuriro", "inkorora", "umutwe", "ububabare", "inda", "impiswi", "kuruka",
    "umunaniro", "guhumeka", "kubura umwuka", "ibimenyetso", "umuganga",
    "ivuriro", "ibitaro", "imiti", "isuzuma", "umwana", "gutwita", "amaraso",
    "umuvuduko", "isukari", "kubyimba", "ikizunguzungu", "gutitira",
)

# A prompt is billed per token on a small free-tier budget, so the 148-term map
# is not worth ~1.8k tokens on every call. Only the terms the conversation
# actually uses are rendered, topped up with the core list above.
GLOSSARY_PROMPT_MAX_TERMS = 48


def glossary_for(text: str, max_terms: int = GLOSSARY_PROMPT_MAX_TERMS) -> str:
    """Compact glossary limited to the terms this conversation can need."""
    lowered = (text or "").lower()
    chosen: List[Tuple[str, str]] = []
    seen: Set[str] = set()

    for term, english in MEDICAL_TERMS.items():
        if term in seen:
            continue
        if term in _CORE_GLOSSARY_TERMS or (
            len(term) >= MIN_TERM_LENGTH and _PATTERNS[term].search(lowered)
        ):
            chosen.append((term, english))
            seen.add(term)

    for term in _CORE_GLOSSARY_TERMS:
        if term in seen or term not in MEDICAL_TERMS:
            continue
        chosen.append((term, MEDICAL_TERMS[term]))
        seen.add(term)

    return "; ".join(f"{rw}={en}" for rw, en in chosen[:max_terms])
