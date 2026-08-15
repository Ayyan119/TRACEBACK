# TRACEBACK Investigation Adapter Layer

## 1. What is an Adapter?
An **Adapter** (Adapter Pattern) is a structural software design pattern that converts the interface of one system into another interface expected by clients. It acts as a translation bridge, allowing two incompatible abstractions—such as a RESTful web API framework (FastAPI) and an autonomous state-graph engine (LangGraph)—to communicate cleanly without either system depending directly on the internal implementation details of the other.

---

## 2. Why TRACEBACK Needs an Adapter
The TRACEBACK platform consists of two distinct domain layers:
1. **The Backend Application Layer**: Responsible for REST API endpoints, Pydantic schemas, database models (SQLAlchemy ORM), MinIO object storage, user sessions, and HTTP transport.
2. **The LangGraph Agent Investigation Layer**: Responsible for state-graph execution (`InvestigationState`), agentic tool loops, Qdrant vector retrieval, vision analysis, reranking, hypothesis evaluation, and multi-node execution traces.

Without an Adapter, API endpoint handlers would have to directly import LangGraph internal primitives (`StateGraph`, `TypedDict` state channels, reducer functions, graph execution trace dicts), creating tight coupling. Changes to the AI agent graph structure would break API endpoints, and changes to database models would break agent state.

The Adapter solves this by providing a strict **boundary layer**.

---

## 3. Core Problems Solved
- **Decoupling**: Keeps FastAPI controllers completely ignorant of LangGraph internals (no imports of `StateGraph`, `START`, `END`, or graph nodes in API routes).
- **Deterministic Testing**: Allows testing API data translation using mock graph runners without invoking real LLM APIs or vector databases.
- **Input Validation**: Ensures mandatory incident logs are provided and attachment bounds (max 10 total attachments, max 3 pages per document, max 2000 description words) are respected before entering the AI graph.
- **Security & Secret Protection**: Catches graph execution exceptions and wraps them in clean application errors without leaking API keys, SQL connection strings, or system paths in HTTP error responses.

---

## 4. Input & Output Data Flow Architecture

```
                          ┌──────────────────────────┐
                          │   TRACEBACK API Controller│
                          └─────────────┬────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │   InvestigationInput Schema  │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │        InputAdapter          │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │   InvestigationState Dict    │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │  LangGraph Agent Workflow    │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │   Final Graph State Dict     │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │        OutputAdapter         │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │  InvestigationResult Schema  │
                        └───────────────┬──────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │   TRACEBACK API Response │
                          └──────────────────────────┘
```

---

## 5. InvestigationState Field Mappings

### Input Translation (`InvestigationInput` -> `InvestigationState`)
| TRACEBACK API / Backend Field | Target `InvestigationState` Field | Transformation Details |
| :--- | :--- | :--- |
| `input_data.incident_id` | `state["incident_id"]` | Incident ticket UUID string |
| `input_data.project_id` | `state["project_id"]` | Parent project UUID string |
| `input_data.incident_description` | `state["incident_description"]` | Main incident report text |
| `input_data.incident_log_reference` | `state["incident_log_reference"]` | Dict `{ "file_name": ..., "file_size_bytes": ... }` |
| `input_data.services` | `state["services"]` | List of target microservice names |
| `input_data.service_metadata` | `state["service_metadata"]` | Microservice configuration dictionary |
| `input_data.incident_documents` | `state["incident_documents"]` | Raw dict list `[{ "name": ..., "content": ... }]` |
| `input_data.incident_images` | `state["incident_images"]` | Raw dict list `[{ "title": ..., "file_url": ... }]` |

### Output Translation (`InvestigationState` -> `InvestigationResult`)
| `InvestigationState` Field | Output `InvestigationResult` Field | Purpose |
| :--- | :--- | :--- |
| `state["investigation_id"]` | `result.investigation_id` | Graph run UUID |
| `state["incident_id"]` | `result.incident_id` | Incident UUID |
| `state["investigation_summary"]` | `result.investigation_summary` | Executive summary statement |
| `state["confidence"]` | `result.confidence` | Root cause confidence score ($0-100\%$) |
| `state["selected_hypothesis"]` | `result.selected_hypothesis` | Primary root cause hypothesis |
| `state["hypotheses"]` | `result.hypotheses` | Full list of candidate hypotheses |
| `state["evidence_analysis"]` | `result.evidence_analysis` | Detailed symptoms and findings |
| `state["accepted_evidence"]` | `result.accepted_evidence` | Validated accepted evidence items |
| `state["rejected_evidence"]` | `result.rejected_evidence` | Discarded irrelevant files & reasons |
| `state["final_report"]` | `result.final_report` | Complete Root Cause Analysis (RCA) document |

---

## 6. Error Handling
The adapter defines dedicated custom exceptions in `exceptions.py`:
- `MissingLogReferenceError`: Raised when the mandatory incident log file reference is omitted.
- `InvalidInputError`: Raised when input validation fails.
- `GraphExecutionError`: Raised when LangGraph fails during execution or produces an unparseable state.

All exceptions prevent credential or internal file path leaks in API responses.

---

## 7. Testing Strategy & Dependency Injection

The `InvestigationAdapter` class accepts an optional `graph_runner` parameter in its constructor:
```python
# Mock Graph Injection for Fast Unit Tests
adapter = InvestigationAdapter(graph_runner=mock_graph_runner)
result = await adapter.arun(input_data)
```
If no `graph_runner` is injected, the adapter lazily imports and compiles the real `build_investigation_graph()` from `langgraph_investigation_agent.app.graph.workflow`.

---

## 8. Why API Code Must Not Contain LangGraph Internals
1. **Separation of Concerns**: REST APIs handle request routing, HTTP headers, authentication, and validation. AI agents handle graph traversal, vector search, and model reasoning.
2. **Maintenance Simplicity**: Refactoring graph nodes or adding new state channels in LangGraph will never break backend API contracts.
3. **Portability**: The LangGraph investigation engine remains a standalone, portable Python package that can be run from CLI scripts, worker tasks, or test suites.
