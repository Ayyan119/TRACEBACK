# TRACEBACK — FastAPI Backend Foundation

"Find what changed. Fix what broke."

TRACEBACK is an AI-powered production incident investigation and root-cause analysis platform. This directory contains the modular FastAPI backend application designed to serve the Next.js frontend (`FastApiClient`).

---

## 1. System Architecture

```
Next.js Frontend (FastApiClient)
         │
         ▼
FastAPI REST API (/api/v1)
         │
 ┌───────┼───────────────────┬────────────────────┐
 │       │                   │                    │
 ▼       ▼                   ▼                    ▼
PostgreSQL (DB)      MinIO (Files)       Qdrant (Vectors)    Redis (Jobs)
```

- **Router (`app/api/v1/endpoints/`):** HTTP request handling, OpenAPI validation, and status codes.
- **Schemas (`app/schemas/`):** Pydantic v2 DTOs for request inputs and response bodies.
- **Services (`app/services/`):** Business logic and orchestration.
- **Repositories (`app/repositories/`):** Pure SQLAlchemy 2.0 database access queries.
- **Models (`app/models/`):** SQLAlchemy ORM declarative models.
- **Db (`app/db/`):** Async SQLAlchemy 2.0 engine, session factory, and session generator.
- **Core (`app/core/`):** Pydantic Settings, RFC-7807 problem details error handling, standard logging.

---

## 2. Getting Started

### Step 1: Create a Virtual Environment
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
# OR using pyproject.toml:
pip install -e ".[test]"
```

### Step 3: Configure Environment Variables
```bash
cp .env.example .env
```

### Step 4: Run FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 3. API Documentation & Interactive Swagger

Once the server is running, open:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check Endpoint:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 4. Running Tests

Execute pytest from the `backend/` directory:

```bash
pytest
```
