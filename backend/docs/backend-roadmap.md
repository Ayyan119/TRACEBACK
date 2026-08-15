# TRACEBACK Backend Module Implementation Roadmap

"Find what changed. Fix what broke."

---

## Architecture Principles
1. **Clean Separation of Concerns:**
   - **Router (`app/api/v1/endpoints/`):** HTTP request/response validation, status codes, OpenAPI docs.
   - **Schemas (`app/schemas/`):** Pydantic v2 input validation & output response DTOs.
   - **Services (`app/services/`):** Core business logic, orchestration, authorization checks.
   - **Repositories (`app/repositories/`):** Pure SQLAlchemy database access and raw queries.
   - **Models (`app/models/`):** SQLAlchemy 2.0 ORM database table definitions.

2. **Strict Project Workspace Isolation:**
   - All relational entities (`services`, `incidents`, `knowledge_documents`, `deployments`, `logs`) contain a mandatory `project_id` foreign key.
   - Every service and repository query filters by `project_id`.

---

## Sequential Phased Roadmap

### PHASE 1: FastAPI Foundation ← [CURRENT COMPLETED PHASE]
- Production-oriented FastAPI application setup.
- Pydantic Settings configuration (`app/core/config.py`).
- RFC-7807 problem details exception system (`app/core/exceptions.py`).
- Standard logging configuration (`app/core/logging.py`).
- SQLAlchemy 2.0 async database session setup (`app/db/session.py`).
- Versioned routing architecture (`/api/v1/health`).
- Pytest testing suite foundation (`tests/test_health.py`).

### PHASE 2: PostgreSQL & SQLAlchemy Domain Models
- Define SQLAlchemy 2.0 ORM models in `app/models/`:
  - `ProjectModel`, `ServiceModel`, `IncidentModel`, `EvidenceModel`, `InvestigationModel`, `HypothesisModel`, `TimelineEventModel`, `RecommendationModel`, `EvidenceGapModel`, `KnowledgeDocumentModel`, `LogEventModel`, `DeploymentModel`.
- Alembic database migration environment initialization (`alembic init`).
- Initial database schema migration generation.

### PHASE 3: Projects Module (CRUD & Export)
- `app/api/v1/endpoints/projects.py`
- Endpoints:
  - `GET /api/v1/projects`
  - `GET /api/v1/projects/{id}`
  - `POST /api/v1/projects`
  - `PATCH /api/v1/projects/{id}`
  - `DELETE /api/v1/projects/{id}`
  - `GET /api/v1/projects/{id}/export`

### PHASE 4: Services & Deployments Module
- `app/api/v1/endpoints/services.py`
- Endpoints:
  - `GET /api/v1/projects/{projectId}/services`
  - `POST /api/v1/services`
  - `PATCH /api/v1/services/{id}`
  - `DELETE /api/v1/services/{id}`

### PHASE 5: Incidents & Evidence Module
- `app/api/v1/endpoints/incidents.py` & `evidence.py`
- Endpoints:
  - `GET /api/v1/projects/{projectId}/incidents`
  - `GET /api/v1/incidents/{id}`
  - `POST /api/v1/incidents`
  - `DELETE /api/v1/incidents/{id}`
  - `GET /api/v1/incidents/{id}/evidence`
  - `POST /api/v1/incidents/{id}/evidence`

### PHASE 6: Logs & Telemetry Stream Module
- `app/api/v1/endpoints/logs.py`
- Endpoints:
  - `GET /api/v1/incidents/{id}/logs`
  - `GET /api/v1/incidents/{id}/logs/statistics`

### PHASE 7: MinIO Object Storage Integration
- MinIO Python Client integration in `app/core/storage.py`.
- Multipart binary file upload storage for raw PDFs, DOCX, log archives.

### PHASE 8: Knowledge Ingestion & Document Processing
- `app/api/v1/endpoints/knowledge.py`
- Endpoints:
  - `GET /api/v1/projects/{projectId}/knowledge`
  - `POST /api/v1/projects/{projectId}/knowledge/documents`
  - `POST /api/v1/knowledge/{id}/retry`
  - `DELETE /api/v1/knowledge/{id}`

### PHASE 9: Qdrant Vector Database & Embeddings Pipeline
- Qdrant Client integration in `app/core/vector.py`.
- SentenceTransformer / BGE embeddings generation for document chunks.

### PHASE 10: RAG (Retrieval-Augmented Generation) Pipeline
- Semantic search context retrieval matching incident symptoms to indexed runbooks.

### PHASE 11: AI Root Cause Investigation Engine
- `app/api/v1/endpoints/investigations.py`
- Endpoints:
  - `GET /api/v1/incidents/{id}/investigation`
  - `POST /api/v1/incidents/{id}/investigate`

### PHASE 12: LangGraph Agent & Tool Execution
- Multi-step investigation state machine with specialized telemetry analysis tools.

### PHASE 13: Redis & Background Task Queue (Celery / ARQ)
- Asynchronous worker queue for long-running document indexing & AI triage jobs.

### PHASE 14: Next.js Frontend Integration
- Switch `NEXT_PUBLIC_API_MODE=real` in Next.js frontend to connect FastAPI endpoints.

### PHASE 15: Authentication & Multi-Tenancy Security
- JWT / OAuth2 authentication middleware & team permissions.

### PHASE 16: End-to-End Testing & Production Deployment
- Docker Compose, Kubernetes manifests, and CI/CD pipelines.
