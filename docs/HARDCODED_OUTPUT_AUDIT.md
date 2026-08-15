# TRACEBACK — Hardcoded / Static Output Audit

## 1. Verdict

**DEFINITELY HARDCODED** (combined with fallback rules, database connection misconfiguration, and missing LLM invocations).

---

## 2. Exact Source of Suspicious Output

The suspicious output ("Missing index on foreign key customer_id...", 94.5% confidence) originates directly from a **hardcoded fallback branch** in Python:

- **Primary File**: [`langgraph_investigation_agent/app/analysis/hypotheses.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/analysis/hypotheses.py#L65-L87)
- **Lines**: 65–87
- **Function**: `generate_ranked_hypotheses()`
- **Code Responsible**:
```python
    else:
        h1 = Hypothesis(
            hypothesis_id="HYP-1",
            title="PostgreSQL Connection Pool Exhaustion due to Unindexed Query Lock Contention",
            description=f"High volume checkout transactions created row-level lock contention on orders table. Connection slots filled up to max_connections=100 limit, causing 504 Gateway Timeouts on {affected_service}.",
            confidence=94.5,
            supporting_evidence_ids=evidence_ids,
            contradicting_evidence_ids=[],
            affected_services=[affected_service, "postgresql_db"],
            likely_root_cause="Missing index on foreign key customer_id causing full table scans and row locks during peak checkout traffic.",
            recommended_next_check="Run EXPLAIN ANALYZE on checkout queries and scale PostgreSQL max_connections from 100 to 250."
        )
```

### Secondary Contributing Sources:

1. **Hardcoded Evidence Symptoms**:
   - **File**: [`langgraph_investigation_agent/app/graph/nodes.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/graph/nodes.py#L315-L321)
   - **Lines**: 315–321 (`analyze_evidence_node`)
   - **Code**: `else:` branch populates symptoms with `"HTTP 504 Gateway Timeout on checkout endpoints"`, `"PostgreSQL active connections maxed at 100/100"`, `"Row-level lock contention on orders table"`.

2. **Hardcoded Synthetic Previous Incident**:
   - **File**: [`langgraph_investigation_agent/app/retrieval/previous_incidents.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/retrieval/previous_incidents.py#L67-L87)
   - **Lines**: 67–87 (`retrieve_previous_incidents`)
   - **Cause**: Checks `if config.QDRANT_URL and config.QDRANT_API_KEY:`. Because local Qdrant container has no API key, `QDRANT_API_KEY` is empty, bypassing Qdrant search and returning a synthetic incident ("Checkout Service Database Lock Contention Outage").

3. **Hardcoded Synthetic Knowledge Chunks**:
   - **File**: [`langgraph_investigation_agent/app/retrieval/qdrant_retriever.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/retrieval/qdrant_retriever.py#L78-L106)
   - **Lines**: 78–106 (`retrieve_knowledge_chunks`)
   - **Cause**: Checks `if config.QDRANT_URL and config.QDRANT_API_KEY:`. Bypasses Qdrant search when `QDRANT_API_KEY` is empty and returns hardcoded PostgreSQL runbooks.

4. **Hardcoded Synthetic Log Records**:
   - **File**: [`langgraph_investigation_agent/app/tools/log_tools.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/tools/log_tools.py#L96-L113)
   - **Lines**: 96–113 (`query_incident_logs`)
   - **Cause**: Default `DATABASE_URL` in `app/config.py` uses `traceback:traceback123@localhost:5432/traceback_db`. The local Docker PostgreSQL container uses `postgres:postgres@localhost:5432/traceback_db`. The DB query fails and silently falls back to synthetic log records containing `"Connection pool exhausted on postgresql://checkout_db."`.

---

## 3. Complete Data Flow

```
USER INPUT (Frontend Incident Description)
    ↓
POST /api/v1/incidents/{incident_id}/investigate
    ↓
AIInvestigationService (creates investigation_run record in PostgreSQL)
    ↓
InvestigationAdapter (converts DTO to InvestigationState)
    ↓
LangGraph Engine (graph.ainvoke)
    ↓
[Node 1: initialize_state] → Dynamic state dict created
    ↓
[Node 2 & 3: process_images & process_documents] → Static keyword matching (No LLM)
    ↓
[Node 4: collect_evidence] → Aggregates description & attachments
    ↓
[Node 5: reason_with_tools] → Hardcoded iteration check (No LLM)
    ↓
[Node 6: execute_log_tools] → Database connection fails (wrong creds) → RETURNS MOCK LOGS ("Connection pool exhausted...")
    ↓
[Node 7: incident_analyzer] → Static keyword check (No LLM)
    ↓
[Node 8 & 9: retrieve_knowledge & retrieve_previous_incidents] → Bypasses Qdrant (missing QDRANT_API_KEY) → RETURNS MOCK QDRANT RUNBOOKS & MOCK INCIDENTS
    ↓
[Node 10: rerank_retrieved_information] → Python keyword loop (No LLM)
    ↓
[Node 11: analyze_evidence] → Falls through to default else: branch → HARDCODED POSTGRESQL SYMPTOMS
    ↓
[Node 12: generate_hypotheses] → Falls through to default else: branch → HARDCODED HYPOTHESIS (94.5% Confidence, "Missing index on foreign key customer_id...")
    ↓
[Node 13: evaluate_hypotheses] → Hardcoded threshold check confidence >= 85 (No LLM)
    ↓
[Node 14: generate_final_report] → Assembles final JSON report from hardcoded state (No LLM)
    ↓
InvestigationAdapter → OutputAdapter → AIInvestigationService
    ↓
Database Persistence → Saves result to PostgreSQL `investigation_runs` & `incidents.root_cause_summary`
    ↓
Frontend Rendering → Displays persistent JSON report
```

---

## 4. LLM Audit

| Node | Provider | Model | Actual LLM Call? | Current Incident Passed? | Static Fallback? |
|---|---|---|---|---|---|
| 1. initialize_state | None | N/A | NO | Yes | Yes (State init) |
| 2. process_images | None | N/A | NO | Yes (Keyword only) | Yes (Hardcoded observations) |
| 3. process_documents | None | N/A | NO | Yes (Keyword only) | Yes (Hardcoded summaries) |
| 4. collect_evidence | None | N/A | NO | Yes | No |
| 5. reason_with_tools | None | N/A | NO | No | Yes (Hardcoded tool decision) |
| 6. execute_log_tools | None | N/A | NO | Yes (Failed DB call) | Yes (Hardcoded log fallback) |
| 7. incident_analyzer | None | N/A | NO | Yes (Keyword only) | Yes (Hardcoded decision) |
| 8. retrieve_knowledge | None | N/A | NO | Yes (Bypassed Qdrant) | Yes (Hardcoded runbooks) |
| 9. retrieve_previous_incidents | None | N/A | NO | Yes (Bypassed Qdrant) | Yes (Hardcoded past incident) |
| 10. rerank_retrieved_info | None | N/A | NO | Yes | No |
| 11. analyze_evidence | None | N/A | NO | Yes (If no "redis"/"oom") | **YES (Hardcoded Postgres symptoms)** |
| 12. generate_hypotheses | None | N/A | NO | Yes (If no "redis"/"oom") | **YES (Hardcoded 94.5% Postgres RCA)** |
| 13. evaluate_hypotheses | None | N/A | NO | Yes | Yes (Hardcoded sufficiency rules) |
| 14. generate_final_report | None | N/A | NO | Yes | Yes (Hardcoded report builder) |

> **CRITICAL FINDING**: **0 LLM calls are made in the entire 14-node LangGraph pipeline**. The helper functions `get_reasoning_llm()` and `get_structured_llm()` in `app/models/llm.py` are never imported or invoked by any node in the system.

---

## 5. Node Audit

| Node | Dynamic? | Hardcoded? | Mock? | Fallback? | Status |
|---|---|---|---|---|---|
| 1. initialize_state | Partial | No | No | No | Operational |
| 2. process_images | No | Yes | Yes | Yes | Hardcoded fallback rules |
| 3. process_documents | No | Yes | Yes | Yes | Hardcoded fallback rules |
| 4. collect_evidence | Yes | No | No | No | Operational |
| 5. reason_with_tools | No | Yes | No | Yes | Hardcoded tool routing |
| 6. execute_log_tools | Yes | Yes | Yes | **YES** | Falls back to mock logs when DB auth fails |
| 7. incident_analyzer | No | Yes | No | Yes | Hardcoded search queries |
| 8. retrieve_knowledge | No | Yes | Yes | **YES** | Falls back to mock runbooks when API key missing |
| 9. retrieve_prev_incidents | No | Yes | Yes | **YES** | Falls back to mock incident when API key missing |
| 10. rerank_retrieved_info | Partial | No | No | No | Operational |
| 11. analyze_evidence | No | **YES** | Yes | **YES** | Hardcoded Postgres symptoms in default branch |
| 12. generate_hypotheses | No | **YES** | Yes | **YES** | **Hardcoded 94.5% Postgres RCA in default branch** |
| 13. evaluate_hypotheses | No | Yes | No | Yes | Hardcoded threshold rules |
| 14. generate_final_report | No | Yes | No | Yes | Hardcoded schema assembler |

---

## 6. Retrieval Audit

### PostgreSQL Log Retrieval (`execute_log_tools_node`)
- **Query Attempted**: `SELECT id, incident_id, project_id, timestamp, level, service, message, source, raw_line FROM log_records WHERE ...`
- **Result**: Fails due to `DATABASE_URL` mismatch (`traceback:traceback123` vs Docker PostgreSQL `postgres:postgres`).
- **Returned Records**: Mock records ("Connection pool exhausted on postgresql://checkout_db.").

### Qdrant Knowledge & History Retrieval (`retrieve_knowledge` / `retrieve_previous_incidents`)
- **Filter**: `project_id`, `source_type`
- **Result**: Bypassed because `QDRANT_API_KEY` is required in the code condition (`if config.QDRANT_URL and config.QDRANT_API_KEY:`), but local Docker Qdrant runs without an API key.
- **Returned Points**: Mock runbooks ("PostgreSQL Connection Pool & Latency Troubleshooting Runbook") and Mock incident ("Checkout Service Database Lock Contention Outage").

---

## 7. Control Experiment Results

Three test incidents were executed against the actual LangGraph graph (`build_investigation_graph()`):

| Incident | Description | Final Root Cause Output | Confidence | Different From Others? |
|---|---|---|---|---|
| **Incident A** | "Parking cameras stopped detecting vehicles. Feed is active but zero parking count detected." | **Missing index on foreign key customer_id causing full table scans and row locks during peak checkout traffic.** | **94.5%** | ❌ **NO (Output is identical to default hardcoded fallback)** |
| **Incident B** | "Redis cache memory usage reached 95% and requests became slow on auth service." | Redis maxmemory threshold reached with non-volatile key TTLs causing blocking LRU eviction delays. | 96.0% | Yes (Matched "redis" keyword branch) |
| **Incident C** | "Payment service webhook requests returning HTTP 500 due to oom crash." | Unclosed HTTP connection handles causing steady heap memory leaks until cgroup kernel OOM killer terminates the pod. | 95.5% | Yes (Matched "oom" keyword branch) |

> **Conclusion from Control Experiment**: Any incident whose description or evidence does not contain the literal strings `"redis"` or `"oom"` (such as "Parking cameras stopped detecting vehicles") falls into the `else:` branch in `hypotheses.py` and produces the exact same static PostgreSQL lock contention / 94.5% confidence output.

---

## 8. Exact Root Cause of the Problem

Different incidents are producing identical RCA results due to a combination of **4 root causes**:

1. **No LLM Model Integration in Graph Nodes**: None of the 14 LangGraph nodes actually invoke an LLM (Gemini, Groq, or HuggingFace). All 14 nodes rely on static Python dictionary structures and keyword matching rules.
2. **Hardcoded Fallback in `hypotheses.py`**: In `generate_ranked_hypotheses()`, any incident description that does not match `"redis"` or `"oom"` falls into an `else:` block that hardcodes the 94.5% confidence PostgreSQL foreign key index hypothesis.
3. **Qdrant Guard Condition Requirement**: `qdrant_retriever.py` and `previous_incidents.py` check `if config.QDRANT_URL and config.QDRANT_API_KEY:`. Because local Docker Qdrant runs on port 6333 without a `QDRANT_API_KEY`, the check fails and returns mock database lock contention runbooks.
4. **Database Connection Mismatch in `log_tools.py`**: `log_tools.py` uses `config.DATABASE_URL`, which defaults to `traceback:traceback123` instead of `postgres:postgres` (the local Docker container user), triggering exception handling that returns mock database connection pool logs.

---

## 9. Recommended Fix (DO NOT IMPLEMENT YET)

When ready to implement, the fixes should be performed in the following order:

1. **Integrate Real LLM Calls into LangGraph Nodes**:
   - Update `generate_hypotheses_node`, `analyze_evidence_node`, `incident_analyzer_node`, and `generate_final_report_node` to use `get_structured_llm()` from `app.models.llm` to dynamically reason over actual incident symptoms, logs, and evidence.
2. **Fix Local Qdrant Retrieval Guard Condition**:
   - Update `qdrant_retriever.py` and `previous_incidents.py` so they connect to local Qdrant when `QDRANT_URL` is set (e.g. `http://localhost:6333`), regardless of whether `QDRANT_API_KEY` is present.
3. **Fix Database Connection URL**:
   - Ensure `DATABASE_URL` in `langgraph_investigation_agent/app/config.py` matches the backend `.env` setting (`postgresql+asyncpg://postgres:postgres@localhost:5432/traceback_db`).
4. **Remove Hardcoded Default RCA Fallbacks**:
   - Replace the static `else:` branch in `hypotheses.py` and `nodes.py` with dynamic model generation and generic unknown error fallback schemas when LLM keys are absent.
