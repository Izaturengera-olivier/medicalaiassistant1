# Clinical Decision Support (CDS)

AI-assisted **clinical decision-support and patient symptom assessment** system.

This product is **not** a doctor, pharmacist, or diagnostic device. It organizes symptoms, retrieves information from **approved** medical sources, and presents structured suggestions. Qualified healthcare professionals remain responsible for diagnosis, prescription, and treatment.

## Features (roadmap)

- Role-based access: patient, doctor, pharmacist, admin
- Natural-language symptom intake with follow-up questions
- RAG over an admin-managed approved-source list
- Structured AI assessments with citations and triage labels
- Doctor review (accept / modify / reject)
- Pharmacist medication-safety checks (no automatic “stop this drug” advice)
- Audit logging and explainability trails

Phase 1 (this increment) delivers **repository structure**, a bootable Django API with `/api/health/`, a React + i18n shell, Docker PostgreSQL, and documentation. Domain models, JWT, consultations, and AI are later phases.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md). Short version:

React (Vite + TypeScript) → Django REST Framework + JWT → PostgreSQL (`pgvector` when RAG is enabled) → pluggable LLM and retriever interfaces.

## Technologies

| Layer | Choice |
| --- | --- |
| Backend | Django 5, Django REST Framework, SimpleJWT, drf-spectacular |
| Frontend | React 18, TypeScript, Vite, React Router, i18next, Axios |
| Database | PostgreSQL 16 with pgvector image |
| AI | Provider interface; default `mock` until Phase 6 |
| RAG | `MedicalRetriever` interface; default mock until Phase 7 |

## Installation

### Prerequisites

- Python 3.12+ (3.13 is fine)
- Node.js 20+
- Docker Desktop (for PostgreSQL) — optional in Phase 1; SQLite is used when `DATABASE_URL` is unset

### Environment variables

```bash
copy .env.example .env
```

On Linux/macOS: `cp .env.example .env`

Never commit `.env`. Put secrets only there. The frontend must not receive `AI_API_KEY`.

### Database setup

```bash
docker compose up -d
```

Phase 1 APIs do not require PostgreSQL. From Phase 2 onward, set `DATABASE_URL` in `.env` to the Compose credentials.

### Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

Health check: [http://127.0.0.1:8000/api/health/](http://127.0.0.1:8000/api/health/)  
OpenAPI UI (empty routes until later phases): [http://127.0.0.1:8000/api/schema/docs/](http://127.0.0.1:8000/api/schema/docs/)

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App: [http://localhost:5173](http://localhost:5173)

### AI / RAG configuration

Leave `AI_PROVIDER=mock` and `EMBEDDING_PROVIDER=mock` until Phases 6–7. Real keys belong in `.env` only.

## Testing

```bash
cd backend
pytest
```

```bash
cd frontend
npm test
```

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design
- [API.md](API.md) — planned REST surface
- [AI_SAFETY.md](AI_SAFETY.md) — medical-safety rules
- [DATABASE.md](DATABASE.md) — ER design

## Security notes

- JWT and object-level permissions start in Phase 3
- CORS is origin-restricted
- Production settings enable HTTPS-oriented cookie flags
- Audit logs start in Phase 2/3
- Do not store API keys in source or in the React bundle

## Medical safety limitations

- Output is **information and decision support**, not a diagnosis
- Urgency labels are **not** a substitute for clinical assessment
- The system must not independently prescribe or tell a patient to stop or change medication
- Evidence is limited to approved sources; missing evidence must not be invented
