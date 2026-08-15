# STAGE13D_AUDIT.md — TRACEBACK System Audit Report

## 1. Executive Summary
This audit provides a comprehensive inspection of the TRACEBACK AI Production SRE Platform, inspecting the 14-node LangGraph Investigation Agent, Adapter Layer, Backend API integration, PostgreSQL log querying engine, Qdrant vector database retrieval pipelines, and frontend React/Next.js components.

---

## 2. Architecture & Service Breakdown

```
┌─────────────────────────────────────────────────────────┐
│              TRACEBACK Frontend Workbench               │
└────────────────────────────┬────────────────────────────┘
                             │  HTTP POST /incidents/{id}/investigate
                             ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI Incidents Endpoint                │
└────────────────────────────┬────────────────────────────┘
                             │  ai_investigation_service
                             ▼
┌─────────────────────────────────────────────────────────┐
│               Investigation Adapter Layer               │
│  (schemas.py, input_adapter.py, output_adapter.py)     │
└────────────────────────────┬────────────────────────────┘
                             │  InvestigationInput -> InvestigationState
                             ▼
┌─────────────────────────────────────────────────────────┐
│          LangGraph Investigation Agent Engine           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 1. initialize_state     2. process_images (parallel)│ │
│ │ 3. process_documents    4. collect_evidence        │ │
│ │ 5. reason_with_tools    6. execute_log_tools (loop)│ │
│ │ 7. incident_analyzer    8. Self-RAG decision       │ │
│ │ 9. retrieve_knowledge  10. retrieve_incidents       │ │
│ │11. rerank_information  12. analyze_evidence         │ │
│ │13. generate_hypotheses 14. evaluate_hypotheses (loop)│
│ │15. generate_final_report                            │ │
│ └─────────────────────────────────────────────────────┘ │
└──────────────┬───────────────────────────┬──────────────┘
               │                           │
               ▼                           ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ PostgreSQL (log_records)  │ │ Qdrant Vector Engine      │
│ - Time / Service Filter   │ │ - knowledge_chunks        │
│ - Parameterized Queries   │ │ - incident_history        │
└───────────────────────────┘ └───────────────────────────┘
```

---

## 3. Real Services vs Test Mocks Audit

| Service Component | Production / Live Runtime | Unit Test Mocking | Audit Findings & Verification |
| :--- | :--- | :--- | :--- |
| **PostgreSQL (`log_records`)** | Async SQLAlchemy + PostgreSQL database | Real async sqlite/postgres in integration tests | Uses parameterized SQL filters preventing injection (`project_id`, `service`, `level`, `timestamp`). |
| **Qdrant Vector DB** | `QdrantClient` (`knowledge_chunks`, `incident_history`) | In-memory `qdrant_client.QdrantClient(":memory:")` for isolated tests | Real payload filtering enforces project isolation (`tenant_id == project_id`). |
| **LLM Provider** | LangChain `init_chat_model` (OpenAI / Gemini / Ollama) | Deterministic fallback heuristics when API keys absent | Supports structured JSON outputs (`with_structured_output`). |
| **Vision Model** | Gemini Vision / GPT-4o Multimodal Vision | Heuristic OCR fallback for synthetic test URLs | Extracts error spikes, status codes, and stack trace text from images. |
| **LangGraph Engine** | StateGraph with 14 nodes, 3 routers | Compiled `StateGraph(InvestigationState)` | Correctly handles parallel node state merging via custom list reducers (`add_lists`). |
| **LangSmith Tracing** | `LANGCHAIN_TRACING_V2=true` | Configured via env variables | Traces node execution steps, durations, and state transitions. |

---

## 4. Specific Component Audit Details

### A. Real Qdrant Usage
- **Collections**:
  1. `knowledge_chunks`: Stores Chunked runbooks, technical specifications, and SDD documents with 1536-dim / 768-dim embeddings.
  2. `incident_history`: Stores atomic JSON representations of resolved historical incidents.
- **Distance Metric**: Cosine similarity (`Distance.COSINE`).
- **Metadata Filters**: `Filter(must=[FieldCondition(key="project_id", match=MatchValue(value=project_id))])` guarantees strict multi-tenant isolation.

### B. Real PostgreSQL Log Usage
- **Table**: `log_records` (indexed on `project_id`, `incident_id`, `service`, `level`, `timestamp`).
- **Tool**: `QueryIncidentLogsTool` in `app/tools/log_tools.py` provides structured querying for SRE investigation.

### C. LangGraph Execution Path
1. `initialize_state`: Sanitizes inputs and defaults loop counters (`tool_iterations=0`, `investigation_iterations=0`).
2. `process_images` & `process_documents`: Execute in parallel via StateGraph branch.
3. `collect_evidence`: Consolidates accepted and rejected candidate artifacts.
4. `reason_with_tools` $\leftrightarrow$ `execute_log_tools`: Iterative tool calling loop (max 5 iterations per cycle).
5. `incident_analyzer`: Self-RAG decision node (`retrieval_required = True / False`).
6. `retrieve_knowledge` $\rightarrow$ `retrieve_previous_incidents` $\rightarrow$ `rerank_retrieved_information`: RAG pipeline.
7. `analyze_evidence` $\rightarrow$ `generate_hypotheses` $\rightarrow$ `evaluate_hypotheses`: Hypothesis evaluation loop (max 3 cycles).
8. `generate_final_report`: Produces structured RCA report.

---

## 5. Discovered Risks & Mitigations

1. **Risk — LLM Rate Limits / API Key Absence**:
   - *Mitigation*: The agent features structured fallback parsers so test execution and UI rendering never fail abruptly.
2. **Risk — Infinite Loops in Tool / Investigation Cycles**:
   - *Mitigation*: Strict conditional routers (`MAX_TOOL_ITERATIONS = 5`, `MAX_INVESTIGATION_ITERATIONS = 3`) guarantee graph termination.
3. **Risk — Credential / Secret Leakage**:
   - *Mitigation*: Exception handling in `InvestigationAdapter` sanitizes all error messages before returning to the frontend.
