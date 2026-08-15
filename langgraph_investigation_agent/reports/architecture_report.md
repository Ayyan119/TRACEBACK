# TRACEBACK AI Investigation Agent — Technical Architecture Report

## 1. Executive Summary
The TRACEBACK AI Investigation Agent is an agentic, Self-RAG investigation engine built using **LangGraph** and **LangChain**. It performs multi-step root-cause analysis by combining:
- Vision model screenshot analysis
- Technical document evidence extraction
- Interactive PostgreSQL structured log tool queries (max 5 iterations)
- Self-RAG conditional Qdrant vector retrieval (top 8 runbook chunks)
- Atomic single-point resolved incident retrieval (top 2 past incidents)
- Cross-encoder reranking
- Ranked hypothesis generation with evidence provenance and confidence scores

---

## 2. Graph State Schema (`InvestigationState`)

```python
class InvestigationState(TypedDict, total=False):
    investigation_id: str
    incident_id: str
    project_id: str
    incident_description: str
    incident_log_reference: Optional[Dict[str, Any]]
    services: List[str]
    service_metadata: Dict[str, Any]
    incident_documents: List[Dict[str, Any]]
    incident_images: List[Dict[str, Any]]
    processed_document_evidence: List[Dict[str, Any]]
    processed_image_evidence: List[Dict[str, Any]]
    accepted_evidence: List[Dict[str, Any]]
    rejected_evidence: List[Dict[str, Any]]
    log_query_history: List[Dict[str, Any]]
    retrieved_logs: List[Dict[str, Any]]
    tool_iterations: int
    tool_decision: Optional[str]
    retrieval_required: bool
    retrieved_knowledge_documents: List[Dict[str, Any]]
    retrieved_previous_incidents: List[Dict[str, Any]]
    reranked_documents: List[Dict[str, Any]]
    evidence_analysis: Optional[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    selected_hypothesis: Optional[Dict[str, Any]]
    confidence: float
    investigation_summary: Optional[str]
    execution_trace: List[Dict[str, Any]]
```

---

## 3. Node-by-Node Explanation

1. `initialize_state_node`: Validates state input, assigns investigation UUID, initializes trace.
2. `process_images_node`: Parallel vision model processing. Rejects non-error assets, retains telemetry screenshots.
3. `process_documents_node`: Parallel document processing. Extracts text and flags error signatures.
4. `collect_evidence_node`: Merges description, mandatory log ref, and relevant evidence into `accepted_evidence`.
5. `reason_with_tools_node`: Determines if PostgreSQL structured log querying is required. Enforces max 5 iterations.
6. `execute_log_tools_node`: Executes parameterized SQL queries against `log_records` table.
7. `incident_analyzer_node`: Self-RAG decision point. Determines if external Qdrant runbooks are required.
8. `retrieve_knowledge_node`: Searches top 8 knowledge chunks in Qdrant Cloud.
9. `retrieve_previous_incidents_node`: Searches top 2 atomic resolved incident JSON points.
10. `rerank_retrieved_information_node`: Reranks candidates and filters low-relevance items (< 0.60 score).
11. `analyze_evidence_node`: Synthesizes evidence into what, when, affected service, and symptoms.
12. `generate_hypotheses_node`: Generates ranked root-cause hypotheses (`HYP-1`, `HYP-2`) with confidence scores.

---

## 4. Conditional Edge Routers

- `route_after_reason_with_tools`: Returns `"execute_log_tools"` if `tool_decision == "query_logs"` and `iterations <= 5`. Otherwise returns `"incident_analyzer"`.
- `route_after_incident_analysis`: Returns `"retrieve_knowledge"` if `retrieval_required == True`. Otherwise skips to `"analyze_evidence"`.

---

## 5. Security & Safety Design
- **No API Keys Hardcoded**: All credentials loaded via `.env`.
- **Parameterized SQL Queries**: All log tools use bound variables (`:project_id`, `:service`, `:limit`) preventing SQL injection.
- **Strict Iteration & Retrieval Bounds**: Max 5 tool iterations, top 8 knowledge chunks, top 2 past incidents.
