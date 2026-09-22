# API

Authentication is JWT (Phase 3). Until then only public health and schema endpoints exist.

Base path: `/api/`

## Implemented in Phase 1

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/health/` | Public | Liveness JSON |
| GET | `/api/schema/` | Public | OpenAPI schema |
| GET | `/api/schema/docs/` | Public | Swagger UI |

## Planned

### Auth

| Method | Path | Access |
| --- | --- | --- |
| POST | `/api/auth/register/` | Public (patient self-register) |
| POST | `/api/auth/login/` | Public |
| POST | `/api/auth/refresh/` | Refresh token |

### Patients

| Method | Path | Access |
| --- | --- | --- |
| GET | `/api/patients/me/` | Authenticated patient (self) |
| PATCH | `/api/patients/me/` | Self |
| GET | `/api/patients/history/` | Self |

### Consultations

| Method | Path | Access |
| --- | --- | --- |
| POST | `/api/consultations/` | Patient |
| GET | `/api/consultations/` | Patient own; doctor assigned |
| GET | `/api/consultations/{id}/` | Same object-level rules |

### AI

| Method | Path | Access |
| --- | --- | --- |
| POST | `/api/ai/analyze-symptoms/` | Consultation owner |
| POST | `/api/ai/follow-up/` | Consultation owner |

Responses must match the structured assessment schema in [AI_SAFETY.md](AI_SAFETY.md).

### Doctors

| Method | Path | Access |
| --- | --- | --- |
| GET | `/api/doctors/patients/` | Assigned patients |
| GET | `/api/doctors/consultations/` | Assigned |
| POST | `/api/doctors/consultations/{id}/review/` | Assigned; accept/modify/reject |

### Pharmacists

| Method | Path | Access |
| --- | --- | --- |
| GET | `/api/pharmacists/prescriptions/` | Authorized prescriptions |
| POST | `/api/pharmacists/medication-check/` | Pharmacist |

### Catalog

| Method | Path | Access |
| --- | --- | --- |
| GET | `/api/medications/` | Authenticated |
| GET | `/api/medications/{id}/` | Authenticated |
| Write variants | same | Admin |

Admin endpoints for users, conditions, knowledge sources, and audit logs will live under `/api/knowledge/`, `/api/medical/`, `/api/audit/`, and `/api/auth/` as those apps grow.

## Conventions

- JSON request/response
- Object-level authorization on every PHI resource
- Validation errors: DRF standard `{ "field": ["message"] }`
- Medical statements that reach the client include `sources` when evidence exists
