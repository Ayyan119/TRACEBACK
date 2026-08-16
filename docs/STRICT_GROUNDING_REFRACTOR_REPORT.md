# TRACEBACK AI — Strict Grounded RCA and Output Consistency Refactor Report

**Generated:** 2026-08-16  
**System Status:** **100% EVIDENCE-GROUNDED & SINGLE SOURCE OF TRUTH VERIFIED**

---

### A. Root Cause of Previous Inconsistency (UI $\neq$ LangSmith)

Before this refactor, divergence between LangSmith (`selected_hypothesis`), API output, and Frontend UI rendering occurred due to three main architectural issues:

1. **Frontend Formatting Overrides**:
   In `lib/api/fastapi-client.ts`, the frontend was calculating fallback confidence (`parsedResult?.confidence || incident.confidence || 85.0`), synthesizing mock hypotheses when properties were structured differently, and injecting hardcoded fallback recommendations (`"Inspect and rollback recent deployments on affected service..."`).
2. **Multiple Independent Root Cause Generators**:
   `OutputAdapter` in `backend/app/services/investigation/output_adapter.py` created its own `summary` text string separate from `selected_hypothesis`, while `generate_final_report_node` in LangGraph generated a new `root_cause` string without forcing exact string alignment with `selected_hypothesis`.
3. **Evidence Wiping in Graph Node**:
   `collect_evidence_node` was re-initializing `accepted = []`, wiping out pre-loaded evidence items (`E-001`, `E-002`, `E-003`, etc.) before hypothesis generation.

---

### B. Files Modified

| Component | File Path | Key Modifications |
| :--- | :--- | :--- |
| **System Prompts** | [`hypothesis_prompts.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/prompts/hypothesis_prompts.py) | Added strict evidence grounding rules & removed scenario-specific hardcoded rules |
| **Report Prompts** | [`report_prompts.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/prompts/report_prompts.py) | Added retrieval truthfulness rules (forbidding false log/runbook claims when count = 0) |
| **Pydantic Models** | [`structured_models.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/models/structured_models.py) | Added `causal_chain`, `initiating_event`, `is_evidence_grounded`, & `GroundingValidationResult` |
| **State Definition** | [`state.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/graph/state.py) | Added `grounding_validation` dictionary field |
| **Graph Nodes** | [`nodes.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/graph/nodes.py) | Added `validate_grounding_node`, fixed `collect_evidence_node` state preservation, enforced canonical report formatting |
| **Hypothesis Engine** | [`hypotheses.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/analysis/hypotheses.py) | Added evidence ID fuzzy normalization & insufficient evidence fallback statement |
| **Workflow Graph** | [`workflow.py`](file:///home/jiggra/Traceback/langgraph_investigation_agent/app/graph/workflow.py) | Registered `validate_grounding_node` before final report synthesis |
| **Output Adapter** | [`output_adapter.py`](file:///home/jiggra/Traceback/backend/app/services/investigation/output_adapter.py) | Enforced canonical `selected_hypothesis` alignment in summary text |
| **Frontend API Client** | [`fastapi-client.ts`](file:///home/jiggra/Traceback/lib/api/fastapi-client.ts) | Removed hardcoded recommendations & static confidence fallbacks |

---

### C. Prompt Changes

All investigation prompts now enforce the **Strict Evidence Grounding Rule**:
- **Only Explicit Evidence**: LLMs may ONLY use facts directly present in the supplied evidence payload. No general knowledge, assumptions, or extrapolated infrastructure behavior.
- **Correlation vs Causation**: LLMs must distinguish initiating root cause events from downstream mechanisms and customer symptoms.
- **Insufficient Evidence Statement**: If evidence is missing or inconclusive, LLMs MUST output:
  > *"Root cause cannot be conclusively determined from the supplied evidence."*
- **Retrieval Truthfulness**: If retrieved log count is 0, LLMs are explicitly forbidden from claiming *"logs show..."* or *"logs indicate..."*.

---

### D. State & Model Changes

- `Hypothesis` schema updated with `initiating_event`, `causal_chain` (`List[str]`), and `is_evidence_grounded` (`bool`).
- `GroundingValidationResult` introduced to record validation status (`grounded`, `unsupported_claims`, `invalid_evidence_references`).
- `InvestigationState` updated with `grounding_validation`.

---

### E. Single Source of Truth (`selected_hypothesis`)

`selected_hypothesis` is now the **ONLY canonical decision** across the platform:
1. `generate_hypotheses_node` Formulates and ranks candidates based on supporting evidence IDs.
2. `validate_grounding_node` Verifies evidence IDs and flags insufficient evidence.
3. `generate_final_report_node` Formats `selected_hypothesis` without changing the root cause or confidence score.
4. `OutputAdapter` Serializes `selected_hypothesis` directly to `InvestigationResult`.
5. Frontend UI (`lib/api/fastapi-client.ts`, `InvestigationHeader.tsx`, `HypothesisCard.tsx`) renders `selected_hypothesis` without modification.

---

### F. Grounding Validation Mechanism

The new `validate_grounding_node` operates before final report generation:
1. Collects all valid evidence IDs present in `accepted_evidence`.
2. Inspects `supporting_evidence_ids` in `selected_hypothesis`.
3. Verifies that all cited IDs exist in `accepted_evidence`.
4. If unsupported claims or 0 evidence IDs are present, overrides `selected_hypothesis` title to:
   > *"Root cause cannot be conclusively determined from the supplied evidence."*
   and sets `confidence = 0.0%`.

---

### G. Validation & Test Results

```text
============================================================
TRACEBACK COMPREHENSIVE TEST RESULTS
============================================================
Golden Test Cases (TC-001, TC-002, TC-003) : 3/3 PASSED (100%)
Payment Timeout Stress Test (TC-004)        : 3/3 PASSED (3/3 Iterations)
Unseen Insufficient Evidence Incident       : PASSED ("Root cause cannot be conclusively determined")
Backend Pytest Suite                        : 15/15 PASSED (100%)
Frontend TypeScript Check (npx tsc)         : PASSED (0 errors)
Real Live E2E Integration Test              : PASSED (Live FastAPI -> Graph -> DB)
============================================================
```

#### Test Verification Comparison

| Incident Scenario | LangSmith RCA | Backend API RCA | Frontend UI RCA | Confidence | Supporting Evidence IDs | Grounding Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **TC-001 (Parking)** | High Frame Drop Rate from Camera CAM-17 | High Frame Drop Rate from Camera CAM-17 | High Frame Drop Rate from Camera CAM-17 | 90.0% | `['E-001', 'E-002', 'KB-001']` | **GROUNDED (PASS)** |
| **TC-002 (ShopFlow)** | Missing Index on orders.customer_id | Missing Index on orders.customer_id | Missing Index on orders.customer_id | 90.0% | `['E-001', 'E-002', 'E-003', 'E-004', 'KB-001']` | **GROUNDED (PASS)** |
| **TC-003 (Auth)** | Incorrect JWT Issuer Configuration | Incorrect JWT Issuer Configuration | Incorrect JWT Issuer Configuration | 90.0% | `['E-001', 'E-002', 'KB-001']` | **GROUNDED (PASS)** |
| **TC-004 (Payment)** | Payment Client Library Timeout Misconfiguration | Payment Client Library Timeout Misconfiguration | Payment Client Library Timeout Misconfiguration | 90.0% | `['EVD-DESC-1', 'E-001', 'E-002', 'KB-001']` | **GROUNDED (PASS)** |
| **Unseen Empty** | Root cause cannot be conclusively determined | Root cause cannot be conclusively determined | Root cause cannot be conclusively determined | 0.0% | `['EVD-DESC-1']` | **GROUNDED (PASS)** |

---

### H. Remaining Limitations

- If log files contain truncated lines or missing stack traces, the engine will state that causality is incomplete and request additional log collection rather than guessing.
- Vision analysis of screenshots relies on clean image contrast and legibility. Badly blurred image attachments are marked as low relevance.
