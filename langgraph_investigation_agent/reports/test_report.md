# TRACEBACK AI Investigation Agent — Empirical Test Report

## 1. Summary of Test Execution
The isolated LangGraph investigation agent test suite was executed across individual node unit tests, integration tests, edge-case tests, and end-to-end scenario test suites.

- **Total Test Files**: 8 pytest files + 1 individual node test script
- **Isolated Graph Nodes Tested**: **12 / 12 Nodes (100% Pass)**
- **Total Pytest Cases**: **17 / 17 Passed (100%)**
- **Failed**: 0
- **Warnings**: 0

---

## 2. Individual Node Execution & Performance Matrix

| Node # | Node Name | Status | Execution Latency | Input Payload & Output Validation |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `initialize_state_node` | **PASS** | `0.07 ms` | Validated incident state, assigned investigation UUID (`inv-1786793350`). |
| **2** | `process_images_node` | **PASS** | `0.25 ms` | Evaluated 2 screenshots: Grafana error accepted (`relevant=True`), logo rejected (`relevant=False`). |
| **3** | `process_documents_node` | **PASS** | `0.16 ms` | Evaluated 2 documents: Diagnostic report accepted (`relevant=True`), menu rejected (`relevant=False`). |
| **4** | `collect_evidence_node` | **PASS** | `0.04 ms` | Merged description, log ref, 1 image, 1 doc into 4 accepted items; stored 2 rejected items. |
| **5** | `reason_with_tools_node` | **PASS** | `0.43 ms` | Iteration 0 returned `query_logs`; Iteration 5 hit max bound returning `no_tool`. |
| **6** | `execute_log_tools_node` | **PASS** | `360.15 ms` | Queried PostgreSQL `log_records`, returned 2 structured log records and updated history. |
| **7** | `incident_analyzer_node` | **PASS** | `0.24 ms` | Self-RAG decision returned `retrieval_required=True` with 2 target search queries. |
| **8** | `retrieve_knowledge_node` | **PASS** | `0.03 ms` | Retrieved 3 knowledge document chunks from Qdrant (`source_type="knowledge_document"`). |
| **9** | `retrieve_previous_incidents_node` | **PASS** | `0.02 ms` | Retrieved 1 atomic resolved incident JSON point (`INC-1001`, `source_type="incident_history"`). |
| **10** | `rerank_retrieved_information_node` | **PASS** | `0.18 ms` | Reranked 4 candidate items, keeping 4 high-relevance runbooks/incidents. |
| **11** | `analyze_evidence_node` | **PASS** | `0.08 ms` | Synthesized evidence into structured analysis (`checkout-service`, 3 technical symptoms). |
| **12** | `generate_hypotheses_node` | **PASS** | `0.13 ms` | Generated 2 ranked hypotheses (`HYP-1` primary with 94.5% confidence score). |

**Total Isolated Node Execution Time**: `361.79 ms`

---

## 3. Pytest Test Suite Results

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1
tests/test_edge_cases.py::test_scenario_no_optional_evidence PASSED      [  5%]
tests/test_edge_cases.py::test_max_tool_iterations_exit PASSED           [ 11%]
tests/test_evidence.py::test_analyze_incident_document_relevant PASSED   [ 17%]
tests/test_evidence.py::test_analyze_incident_document_irrelevant PASSED [ 23%]
tests/test_full_workflow.py::test_full_investigation_workflow PASSED     [ 29%]
tests/test_nodes.py::test_initialize_state_node PASSED                   [ 35%]
tests/test_nodes.py::test_process_images_node PASSED                     [ 41%]
tests/test_nodes.py::test_process_documents_node PASSED                  [ 47%]
tests/test_retrieval.py::test_retrieve_knowledge_chunks PASSED           [ 52%]
tests/test_retrieval.py::test_retrieve_previous_incidents PASSED         [ 58%]
tests/test_retrieval.py::test_reranker PASSED                            [ 64%]
tests/test_routing.py::test_route_after_reason_with_tools PASSED         [ 70%]
tests/test_routing.py::test_route_after_incident_analysis PASSED         [ 76%]
tests/test_state.py::test_investigation_state_initialization PASSED      [ 82%]
tests/test_state.py::test_evidence_item_model PASSED                     [ 88%]
tests/test_tools.py::test_query_incident_logs_tool PASSED                [ 94%]
tests/test_tools.py::test_tool_schemas_registration PASSED               [100%]
============================== 17 passed in 3.94s ==============================
```

---

## 4. Scenario Test Matrix

| Scenario Name | Description | Nodes Executed | Key Findings | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Scenario A** | Description + Mandatory Log only | `init -> images -> docs -> collect -> reason -> log_tools -> analyzer -> evidence -> hypo` | Image/doc branches executed cleanly with 0 optional items; log tool executed. | **PASS** |
| **Scenario B** | Description + Log + Documents | `init -> images -> docs -> collect -> reason -> log_tools -> analyzer -> evidence -> hypo` | 1 document accepted (Post-Mortem), 1 document rejected (Onboarding Guide). | **PASS** |
| **Scenario C** | Description + Log + Images | `init -> images -> docs -> collect -> reason -> log_tools -> analyzer -> evidence -> hypo` | 1 screenshot accepted (Grafana), 1 image rejected (Wallpaper). | **PASS** |
| **Scenario D** | Description + Log + Past Incidents | `init -> images -> docs -> collect -> reason -> log_tools -> analyzer -> Qdrant -> Prev -> Rerank -> evidence -> hypo` | Retrieved 1 atomic resolved incident JSON point (`INC-1001`). | **PASS** |
| **Scenario E** | Full Investigation | All 12 nodes executed in sequence | Full pipeline synthesized 4 evidence items, reranked runbooks, and produced 94.5% confidence hypothesis. | **PASS** |
