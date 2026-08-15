# STAGE14_DOCUMENTATION.md — Production Investigation Persistence, History, Observability & RCA Lifecycle

## 1. Executive Summary
Stage 14 transforms the TRACEBACK AI root-cause investigation engine into a persistent, traceable, repeatable, and multi-tenant historical platform.

When an AI investigation runs:
1. A new `InvestigationModel` record is created in PostgreSQL with status `CREATED` and an incremented `investigation_number`.
2. Status transitions to `RUNNING`.
3. The 14-node LangGraph investigation workflow runs via `InvestigationAdapter`.
4. Upon successful RCA completion, the record transitions to `COMPLETED` and stores full JSON artifacts (`final_report`, `selected_hypothesis`, `hypotheses`, `accepted_evidence`, `rejected_evidence`, `execution_trace`, duration).
5. The incident record in PostgreSQL updates to `status="Identified"`.
6. `IncidentHistoryService` constructs an **atomic JSON object** of the completed incident, embeds it into a dense vector, and **upserts ONE atomic vector point into Qdrant** (`incident_history` collection).
7. Future AI investigations running the `retrieve_previous_incidents` node query Qdrant and retrieve this complete atomic JSON payload as historical context!

---

## 2. Persistence Model & Schema
**Table Name**: `investigations`

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `VARCHAR(64)` | Unique UUID primary key string |
| `incident_id` | `VARCHAR(64)` | Foreign Key to `incidents.id` |
| `project_id` | `VARCHAR(64)` | Foreign Key to `projects.id` (multi-tenant isolation) |
| `investigation_number` | `INTEGER` | Sequential run number for the incident (1, 2, 3...) |
| `status` | `VARCHAR(32)` | Lifecycle status: `CREATED`, `RUNNING`, `COMPLETED`, `FAILED` |
| `started_at` | `TIMESTAMP` | Timestamp when run started |
| `completed_at` | `TIMESTAMP` | Timestamp when run finished |
| `duration_ms` | `FLOAT` | Total run duration in milliseconds |
| `incident_description` | `TEXT` | Symptom description |
| `final_summary` | `TEXT` | Executive RCA summary statement |
| `root_cause` | `TEXT` | Primary root cause title |
| `confidence` | `FLOAT` | Confidence score (0 - 100%) |
| `final_report_json` | `JSON` | Complete structured RCA report payload |
| `selected_hypothesis_json`| `JSON` | Primary accepted root cause hypothesis payload |
| `hypotheses_json` | `JSON` | All candidate hypotheses evaluated |
| `accepted_evidence_json` | `JSON` | List of accepted evidence items |
| `rejected_evidence_json` | `JSON` | List of rejected evidence items with reasons |
| `execution_trace_json` | `JSON` | Node-by-node execution trace |
| `error_message` | `TEXT` | Sanitized error message if status = `FAILED` |

---

## 3. Investigation Lifecycle State Machine

```
CREATED
  │
  ▼
RUNNING ────(Error)────► FAILED (Error sanitized, duration recorded)
  │
  ▼
COMPLETED (Persists RCA JSON, updates incident, indexes Qdrant history)
```

---

## 4. Atomic Incident History & Qdrant Upsert Architecture

- **Unfragmented Serialization**: A completed incident is represented as a single, complete JSON object. It is **never chunked**.
- **Vector Point Mapping**: Exactly 1 Qdrant vector point per canonical resolved incident.
- **Idempotency**: Qdrant point UUID is derived deterministically from `SHA256("incident_history:" + incident_id)`. Re-indexing updates/upserts the existing vector point without creating duplicate points.
- **Project Isolation**: Qdrant queries enforce payload match `project_id == target_project_id`.

---

## 5. API Endpoints
- `POST /api/v1/incidents/{incident_id}/investigate`: Triggers new investigation run, returns updated incident.
- `GET /api/v1/incidents/{incident_id}/investigations`: Returns all historical runs for an incident (`List[InvestigationRunResponse]`).
- `GET /api/v1/incidents/{incident_id}/investigations/{investigation_id}`: Returns single detailed investigation run.

---

## 6. Verification Results
- **Stage 14 Test Suite**: 4 / 4 PASSED
- **Backend Pytest Suite**: 119 / 119 PASSED (100%)
- **TypeScript**: 0 errors (PASS)
- **Next.js Production Build**: Success (PASS)
