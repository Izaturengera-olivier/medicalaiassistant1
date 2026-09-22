# Architecture

## Purpose

A full-stack clinical decision-support system. Patients describe symptoms in natural language. The backend extracts symptoms, may ask follow-up questions, retrieves passages from an **approved** knowledge base, and asks an LLM for a **structured** assessment. Doctors and pharmacists review and remain accountable.

## Logical pipeline

```
Patient input
  → Symptom extraction
  → Follow-up questions (until enough information)
  → Medical retrieval (approved sources only)
  → Trusted-source filter
  → LLM analysis (structured JSON)
  → Safety / triage validation
  → Patient / doctor / pharmacist UI
```

## Repository layout

```
clinical-cds/
  backend/
    config/                 # Django project (settings, urls, health, OpenAPI)
    accounts/               # User identity and roles
    patients/
    doctors/
    pharmacists/
    consultations/          # Sessions, symptoms, follow-ups, assessments
    medical/                # Condition catalog
    medications/            # Drugs, interactions, prescriptions
    ai/                     # LLM providers, AI services
    knowledge/              # Sources, documents, chunks, retrievers
    audit/
  frontend/
    src/
      components/
      pages/                # patient, doctor, pharmacist, admin
      layouts/
      services/
      hooks/
      context/
      types/
      utils/
      routes/
      i18n/                 # en + rw; no hard-coded UI copy
  docker-compose.yml        # PostgreSQL + pgvector
```

## Backend principles

- Django apps own their models, serializers, views, urls, permissions, and tests
- Business logic lives in `services/` (AIService, SymptomAnalysisService, MedicalRetrievalService, TriageService, MedicationSafetyService)
- Views stay thin
- LLM and retrieval are **interfaces** with mock implementations until keys and corpus exist

## Frontend principles

- Vite + React + TypeScript
- Role dashboards isolated under `pages/`
- All user-visible strings go through i18next (`en`, `rw`)
- Axios client in `services/api.ts`; no secrets in the browser

## Trust boundary

| Trusted | Untrusted |
| --- | --- |
| Admin-approved knowledge sources | Arbitrary web pages |
| Authenticated API with object-level checks (Phase 3+) | Client-supplied “I am a doctor” claims |
| Structured model output validated against a schema | Free-form model text as clinical truth |

## Deployment sketch (later)

- Reverse proxy terminates TLS
- Django `production` settings
- PostgreSQL with restricted roles
- Frontend static assets behind the same origin or CORS allow-list
