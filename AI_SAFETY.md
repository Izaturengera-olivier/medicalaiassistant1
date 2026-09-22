# AI safety

## Product boundary

This system is clinical **decision support** and health **information**. It must not:

- Claim to be a doctor or pharmacist
- Confirm a diagnosis
- Independently prescribe medication
- Tell a patient to stop, start, or change a drug
- Tell a patient to skip professional care
- Invent medications, dosages, guidelines, or sources
- Treat random internet pages as evidence

Professionals remain responsible for diagnosis, prescription, and treatment.

## System instructions (to be enforced in Phase 6)

The model must:

- Use structured JSON, not uncontrolled prose as the primary output
- Distinguish information from diagnosis
- Express uncertainty; never claim certainty when evidence is weak
- Cite retrieved sources on important medical statements
- Ask follow-up questions when data is insufficient
- Surface emergency warning signs and urge urgent professional care when indicated
- Consider allergies and medication history when present
- Refuse when approved evidence is missing rather than hallucinating

## Assessment schema

```json
{
  "symptoms_identified": [],
  "follow_up_questions": [],
  "possible_conditions": [],
  "warning_signs": [],
  "urgency_level": "",
  "general_information": "",
  "medication_information": [],
  "recommended_next_step": "",
  "sources": []
}
```

Urgency values:

- `INFORMATIONAL`
- `ROUTINE_CONSULTATION`
- `PROMPT_MEDICAL_REVIEW`
- `URGENT_MEDICAL_ATTENTION`

Urgency is **not** a diagnosis and must not be presented as one.

Possible conditions are **differentials**, labeled as possible, never confirmed.

## Retrieval rules

- Only admin-approved sources (WHO, Rwanda MoH, Rwanda FDA, recognized institutions, peer-reviewed literature, official guidelines and drug information)
- Store URL, title, publication date if known, retrieval date, and extracted passage
- Filter before the LLM; unapproved documents never enter the prompt
- Provider-agnostic `MedicalRetriever` (`search`, `retrieve`, `rank`, `get_sources`)

## Medication safety

Pharmacist-facing checks may report potential interactions, contraindications, and allergy conflicts with severity **when supported by sources**. Patient-facing copy must not instruct stopping or changing medication. Recommendation is always: review with a qualified professional.

## Logging / explainability

Each assessment stores: actor and consultation ids, input, retrieved evidence, sources, model id, timestamps, safety-check results, and later professional reviews/corrections.

## Evaluation (Phase 11)

Synthetic cases only: common symptoms, multiple differentials, missing data, contradictions, red flags, interactions, allergies, ambiguity. No real patient data without authorization.
