"""Kinyarwanda medical terminology shared by retrieval and prompt building.

Approved sources publish in English, so a Kinyarwanda question has to carry its
English equivalents before it can match anything. The same map keeps the model's
Kinyarwanda terminology consistent when it answers.
"""

from typing import Dict, List
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

    # Conditions & Pathologies
    "malariya": "malaria plasmodium fever",
    "diabeti": "diabetes blood sugar hyperglycemia",
    "isukari": "diabetes blood sugar glucose",
    "umuvuduko": "blood pressure hypertension cardiovascular",
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

    # Care and clinical vocabulary
    "imiti": "medicine drugs medication prescription pharmaceutical",
    "umuti": "medicine drug medication prescription",
    "urukingo": "vaccine vaccination immunization",
    "isuzuma": "examination assessment diagnosis screening",
    "gusuzuma": "examine assess diagnose screen",
    "ibimenyetso": "symptoms signs manifestations indicators",
    "ikimenyetso": "symptom sign manifestation indicator",
    "umuganga": "doctor clinician physician medical officer",
    "farumasi": "pharmacy pharmacist medication drug store",
    "ibitaro": "hospital medical center inpatient",
    "ivuriro": "health centre clinic outpatient healthcare facility",
    "gutwita": "pregnancy pregnant maternal gestation",
    "kubyara": "childbirth delivery obstetrics labor",
    "umwana": "child infant paediatric pediatric newborn",
    "umubyeyi": "mother parent maternal",
    "amaraso make": "anaemia anemia low hemoglobin",
    "akaga": "emergency warning signs danger crisis",
    "ubwihutirwe": "urgency emergency prompt review",
    "inyongera": "supplement follow-up vitamin",
    "ebola": "ebola viral haemorrhagic fever filovirus",
    "kurinda": "prevention prevent protective measures",
    "yirinda": "prevention prevent protect yourself avoid",
    "gukingira": "prevention protect shield avoid",
}

MIN_TERM_LENGTH = 4

# Keys that must appear as a standalone word, because as a substring they also
# occur inside unrelated verb stems (see MEDICAL_TERMS above).
WHOLE_WORD_TERMS = frozenset({"inda"})


def _term_pattern(term: str) -> re.Pattern:
    escaped = re.escape(term)
    if term in WHOLE_WORD_TERMS:
        return re.compile(f"(?<![a-z]){escaped}(?![a-z])")
    return re.compile(escaped)


_PATTERNS = {term: _term_pattern(term) for term in MEDICAL_TERMS}


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
