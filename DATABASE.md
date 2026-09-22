# Database design

Phase 2 will implement these Django models. Phase 1 has empty `models.py` files so apps install cleanly.

Engine: PostgreSQL 16. Vector search: `pgvector` (pluggable; mock retriever until Phase 7).

Time zone: `Africa/Kigali`. All tables use `created_at` / `updated_at` where mutable.

## Entity-relationship (logical)

```
User 1──1 PatientProfile
User 1──1 DoctorProfile
User 1──1 PharmacistProfile

PatientProfile 1──* MedicalHistory
PatientProfile 1──* Consultation
DoctorProfile  1──* Consultation (optional assignee)

Consultation 1──* PatientSymptom
Consultation 1──* FollowUpQuestion
Consultation 1──1 AIAssessment
Consultation 1──* Prescription
Consultation 1──1 DoctorReview (when completed)

Symptom *──* PatientSymptom (catalog optional)

AIAssessment 1──* PossibleCondition
AIAssessment 1──* RetrievedEvidence
PossibleCondition *──1 MedicalCondition (catalog, nullable)

Medication 1──* MedicationInteraction (pair)
Prescription 1──* PrescriptionMedication ──* Medication
Prescription 1──* PharmacistReview

MedicalKnowledgeSource 1──* Document 1──* Chunk 1──1 Embedding
RetrievedEvidence *──1 Chunk (or stored passage snapshot)
RetrievedEvidence *──1 MedicalKnowledgeSource

User 1──* AuditLog
```

## Tables and constraints (summary)

| Model | Key fields | Constraints / indexes |
| --- | --- | --- |
| User | email, password hash, role | Unique email; role ∈ {PATIENT, DOCTOR, PHARMACIST, ADMIN} |
| PatientProfile | user, demographics, language | OneToOne user |
| DoctorProfile | user, license, specialty | OneToOne user |
| PharmacistProfile | user, license | OneToOne user |
| MedicalHistory | patient, allergies, conditions, notes | Indexed by patient |
| Consultation | patient, doctor, status, language | Index (patient, created_at); status workflow |
| Symptom | code, name_en, name_rw | Unique code |
| PatientSymptom | consultation, text, extracted_name, onset | Index consultation |
| FollowUpQuestion | consultation, question, answer, asked_at | Index consultation |
| AIAssessment | consultation, payload JSON, urgency, model | One assessment per analysis version; store input snapshot |
| PossibleCondition | assessment, condition, likelihood_note | Not a confirmed diagnosis |
| MedicalCondition | code, name, description, source | Unique code |
| Medication | name, generic, class, indications, contraindications, precautions, source, verified_at | Unique name+generic where practical |
| MedicationInteraction | med_a, med_b, type, severity, source | Unique unordered pair |
| Prescription | consultation, doctor, status | |
| PrescriptionMedication | prescription, medication, sig text | No auto-dispense |
| MedicalKnowledgeSource | title, url, publisher, approved, published_at | Unique url; approved flag required for RAG |
| Document / Chunk / Embedding | source, text, vector, retrieved_at | Chunk index by source; vector column |
| RetrievedEvidence | assessment, chunk/source, excerpt | Explainability trail |
| DoctorReview | consultation, decision, diagnosis, notes | decision ∈ accept/modify/reject |
| PharmacistReview | prescription, notes, flags | |
| AuditLog | actor, action, object_type, object_id, metadata | Append-only; index actor+created_at |

## PHI notes

- Minimize fields on User; clinical detail lives on PatientProfile / history / consultation
- Object-level permissions must key off patient ownership, doctor assignment, and pharmacist prescription authorization
- Soft-delete only where legally required; audit log is not rewritten
