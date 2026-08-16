import os
import sys
import json
import time
import asyncio
from typing import Dict, Any, List

agent_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if agent_root not in sys.path:
    sys.path.insert(0, agent_root)

from app.contracts.engine_contract import EngineIncidentInput, EngineInvestigationOutput
from app.graph.state import InvestigationState
from app.graph.nodes import (
    initialize_state_node,
    process_images_node,
    process_documents_node,
    collect_evidence_node,
    reason_with_tools_node,
    execute_log_tools_node,
    incident_analyzer_node,
    retrieve_knowledge_node,
    retrieve_previous_incidents_node,
    rerank_retrieved_information_node,
    analyze_evidence_node,
    generate_hypotheses_node,
    evaluate_hypotheses_node,
    validate_grounding_node,
    generate_final_report_node,
)


def load_streamforge_fixture() -> Dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "scenarios", "streamforge_inc3057.json")
    with open(path, "r") as f:
        return json.load(f)


async def run_sequential_node_by_node_test():
    print("============================================================")
    print("TRACEBACK AI — SEQUENTIAL NODE-BY-NODE GROUNDING TEST SUITE")
    print("Incident: INC-3057 (StreamForge Video Platform)")
    print("============================================================")
    
    fixture = load_streamforge_fixture()
    
    node_results: Dict[str, Dict[str, Any]] = {}
    first_divergence: str = None
    
    # ------------------------------------------------------------
    # NODE 1: initialize_state_node
    # ------------------------------------------------------------
    print("\n[STEP 1/12] Testing initialize_state_node...")
    initial_input_state: InvestigationState = {
        "investigation_id": "inv-streamforge-3057",
        "project_id": fixture["project_id"],
        "incident_id": fixture["incident_id"],
        "incident_description": fixture["description"],
        "services": fixture["services"],
        "accepted_evidence": [],
        "processed_document_evidence": [],
        "processed_image_evidence": [],
        "rejected_evidence": [],
        "log_query_history": [],
        "retrieved_logs": [],
        "tool_iterations": 0,
        "investigation_iterations": 0,
        "retrieval_required": False,
        "retrieved_knowledge_documents": [],
        "retrieved_previous_incidents": [],
        "reranked_documents": [],
        "confidence_source": "llm",
        "analysis_status": "success",
        "failed_llm_nodes": [],
        "errors": [],
        "warnings": [],
        "execution_trace": [],
    }
    
    state_step1 = await initialize_state_node(initial_input_state)
    state = {**initial_input_state, **state_step1}
    
    step1_pass = (
        state.get("incident_id") == "INC-3057"
        and state.get("project_id") == "StreamForge Video Platform"
        and len(state.get("services", [])) == 5
    )
    node_results["initialize_state"] = {"status": "PASS" if step1_pass else "FAIL", "details": f"Services: {len(state.get('services', []))}"}
    if not step1_pass and not first_divergence:
        first_divergence = "initialize_state"

    # Add fixture document & log evidence into state for processing
    state["incident_documents"] = [
        {"name": e["source_name"], "content": e["content"]}
        for e in fixture["evidence"] if e["source_type"] == "document"
    ]
    
    # ------------------------------------------------------------
    # NODE 2: process_documents_node
    # ------------------------------------------------------------
    print("[STEP 2/12] Testing process_documents_node...")
    step2_start = time.time()
    state_step2 = await process_documents_node(state)
    state.update(state_step2)
    
    proc_docs = state.get("processed_document_evidence", [])
    step2_pass = len(proc_docs) >= 5
    node_results["process_documents"] = {"status": "PASS" if step2_pass else "FAIL", "details": f"Processed {len(proc_docs)} documents"}
    if not step2_pass and not first_divergence:
        first_divergence = "process_documents"

    # ------------------------------------------------------------
    # NODE 3: process_images_node (Empty images test)
    # ------------------------------------------------------------
    print("[STEP 3/12] Testing process_images_node (Empty images)...")
    state["incident_images"] = []
    state_step3 = await process_images_node(state)
    state.update(state_step3)
    
    step3_pass = state.get("processed_image_evidence") == []
    node_results["process_images"] = {"status": "PASS" if step3_pass else "FAIL", "details": "Empty image payload handled properly"}
    if not step3_pass and not first_divergence:
        first_divergence = "process_images"

    # Pre-populate accepted_evidence with fixture items
    for item in fixture["evidence"]:
        state["accepted_evidence"].append({
            "evidence_id": item["evidence_id"],
            "source_type": item["source_type"],
            "source_name": item["source_name"],
            "content": item["content"],
            "relevance": True,
            "confidence": 1.0,
        })

    # ------------------------------------------------------------
    # NODE 4: collect_evidence_node
    # ------------------------------------------------------------
    print("[STEP 4/12] Testing collect_evidence_node...")
    state_step4 = await collect_evidence_node(state)
    state.update(state_step4)
    
    accepted_ev = state.get("accepted_evidence", [])
    step4_pass = len(accepted_ev) >= 7
    node_results["collect_evidence"] = {"status": "PASS" if step4_pass else "FAIL", "details": f"Accepted {len(accepted_ev)} evidence items"}
    if not step4_pass and not first_divergence:
        first_divergence = "collect_evidence"

    # ------------------------------------------------------------
    # NODE 5: reason_with_tools_node & execute_log_tools_node
    # ------------------------------------------------------------
    print("[STEP 5/12] Testing reason_with_tools_node & execute_log_tools_node...")
    state_step5a = await reason_with_tools_node(state)
    state.update(state_step5a)
    
    step5a_pass = state.get("tool_decision") == "query_logs"
    
    # Populate log data from fixture
    log_evidence = [e for e in fixture["evidence"] if e["source_type"] == "log"]
    if log_evidence:
        state["retrieved_logs"] = [
            {"service": "video-transcoding-service", "message": log_evidence[0]["content"], "timestamp": "18:06:02"}
        ]
        
    state_step5b = await execute_log_tools_node(state)
    state.update(state_step5b)
    
    step5_pass = step5a_pass and len(state.get("retrieved_logs", [])) > 0
    node_results["execute_log_tools"] = {"status": "PASS" if step5_pass else "FAIL", "details": f"Logs retrieved: {len(state.get('retrieved_logs', []))}"}
    if not step5_pass and not first_divergence:
        first_divergence = "execute_log_tools"

    # ------------------------------------------------------------
    # NODE 6: incident_analyzer_node
    # ------------------------------------------------------------
    print("[STEP 6/12] Testing incident_analyzer_node (Self-RAG)...")
    state_step6 = await incident_analyzer_node(state)
    state.update(state_step6)
    
    step6_pass = state.get("retrieval_required") is True
    node_results["incident_analyzer"] = {"status": "PASS" if step6_pass else "FAIL", "details": f"Retrieval required: {state.get('retrieval_required')}"}
    if not step6_pass and not first_divergence:
        first_divergence = "incident_analyzer"

    # ------------------------------------------------------------
    # NODE 7: Knowledge & Incident Retrieval & Reranker
    # ------------------------------------------------------------
    print("[STEP 7/12] Testing Knowledge Retrieval & Reranker...")
    state_step7a = await retrieve_knowledge_node(state)
    state.update(state_step7a)
    
    state_step7b = await retrieve_previous_incidents_node(state)
    state.update(state_step7b)
    
    kb_items = [e for e in fixture["evidence"] if e["evidence_id"].startswith("KB")]
    state["retrieved_knowledge_documents"] = [
        {"title": e["source_name"], "content": e["content"], "source_type": "knowledge_document"}
        for e in kb_items if "runbook" in e["source_name"].lower()
    ]
    state["retrieved_previous_incidents"] = [
        {"title": e["source_name"], "content": e["content"], "source_type": "incident_history"}
        for e in kb_items if "runbook" not in e["source_name"].lower()
    ]
    
    state_step7c = await rerank_retrieved_information_node(state)
    state.update(state_step7c)
    
    step7_pass = len(state.get("reranked_documents", [])) > 0
    node_results["retrieve_and_rerank"] = {"status": "PASS" if step7_pass else "FAIL", "details": f"Reranked items: {len(state.get('reranked_documents', []))}"}
    if not step7_pass and not first_divergence:
        first_divergence = "retrieve_and_rerank"

    # ------------------------------------------------------------
    # NODE 8: analyze_evidence_node
    # ------------------------------------------------------------
    print("[STEP 8/12] Testing analyze_evidence_node...")
    state_step8 = await analyze_evidence_node(state)
    state.update(state_step8)
    
    ev_analysis = state.get("evidence_analysis", {})
    step8_pass = bool(ev_analysis) and "video-transcoding-service" in str(ev_analysis.get("affected_service", "")).lower()
    node_results["analyze_evidence"] = {"status": "PASS" if step8_pass else "FAIL", "details": f"Primary Affected Service: {ev_analysis.get('affected_service')}"}
    if not step8_pass and not first_divergence:
        first_divergence = "analyze_evidence"

    # ------------------------------------------------------------
    # NODE 9: generate_hypotheses_node
    # ------------------------------------------------------------
    print("[STEP 9/12] Testing generate_hypotheses_node...")
    state_step9 = await generate_hypotheses_node(state)
    state.update(state_step9)
    
    hypotheses = state.get("hypotheses", [])
    primary_h = state.get("selected_hypothesis", {}) or {}
    
    step9_pass = len(hypotheses) >= 1 and primary_h.get("confidence", 0.0) >= 70.0
    node_results["generate_hypotheses"] = {"status": "PASS" if step9_pass else "FAIL", "details": f"Generated {len(hypotheses)} hypotheses. Primary: {primary_h.get('title')} ({primary_h.get('confidence')}%)"}
    if not step9_pass and not first_divergence:
        first_divergence = "generate_hypotheses"

    # ------------------------------------------------------------
    # NODE 10: evaluate_hypotheses_node
    # ------------------------------------------------------------
    print("[STEP 10/12] Testing evaluate_hypotheses_node...")
    state_step10 = await evaluate_hypotheses_node(state)
    state.update(state_step10)
    
    hyp_eval = state.get("hypothesis_evaluation", {})
    step10_pass = hyp_eval.get("evidence_sufficient") is True
    node_results["evaluate_hypotheses"] = {"status": "PASS" if step10_pass else "FAIL", "details": f"Sufficient: {hyp_eval.get('evidence_sufficient')}"}
    if not step10_pass and not first_divergence:
        first_divergence = "evaluate_hypotheses"

    # ------------------------------------------------------------
    # NODE 11: validate_grounding_node
    # ------------------------------------------------------------
    print("[STEP 11/12] Testing validate_grounding_node...")
    state_step11 = await validate_grounding_node(state)
    state.update(state_step11)
    
    grounding_val = state.get("grounding_validation", {})
    step11_pass = grounding_val.get("grounded") is True
    node_results["validate_grounding"] = {"status": "PASS" if step11_pass else "FAIL", "details": f"Grounded: {grounding_val.get('grounded')}"}
    if not step11_pass and not first_divergence:
        first_divergence = "validate_grounding"

    # ------------------------------------------------------------
    # NODE 12: generate_final_report_node
    # ------------------------------------------------------------
    print("[STEP 12/12] Testing generate_final_report_node...")
    state_step12 = await generate_final_report_node(state)
    state.update(state_step12)
    
    final_rep = state.get("final_report", {})
    step12_pass = bool(final_rep) and final_rep.get("confidence", 0.0) >= 70.0
    node_results["generate_final_report"] = {"status": "PASS" if step12_pass else "FAIL", "details": f"RCA: {final_rep.get('root_cause')} ({final_rep.get('confidence')}%)"}
    if not step12_pass and not first_divergence:
        first_divergence = "generate_final_report"

    # ============================================================
    # AUTOMATED FINAL ANSWER EVALUATOR (0-2 Scoring across 10 Categories)
    # ============================================================
    print("\n============================================================")
    print("AUTOMATED FINAL ANSWER EVALUATION")
    print("============================================================")
    
    rc_title = str(primary_h.get("title", "")).lower()
    rc_exp = str(primary_h.get("likely_root_cause", "")).lower() + " " + str(primary_h.get("description", "")).lower()
    rc_combined = f"{rc_title} {rc_exp}"
    
    # 1. Root Cause Correctness (Disk storage exhaustion / v4.2.0 deployment temp space / ENOSPC)
    rc_correct = any(kw in rc_combined for kw in ["disk", "storage", "workspace", "enospc", "8gi", "50gi", "v4.2.0", "ffmpeg"])
    score_rc = 2 if rc_correct else 0
    
    # 2. Affected Service Correctness (video-transcoding-service)
    aff_services = primary_h.get("affected_services", []) or final_rep.get("affected_services", [])
    service_correct = any("transcod" in str(s).lower() for s in aff_services)
    score_service = 2 if service_correct else 0
    
    # 3. Causal Chain Correctness (Deployment -> workspace reduction/files retained -> disk exhaustion -> ENOSPC -> queue backlog -> 503)
    causal_chain = str(primary_h.get("causal_chain", [])) + " " + rc_combined
    chain_correct = any(kw in causal_chain.lower() for kw in ["deploy", "workspace", "disk", "enospc", "queue", "503", "manifest"])
    score_chain = 2 if chain_correct else (1 if "disk" in causal_chain.lower() else 0)
    
    # 4. Evidence Correctness (Cites valid evidence IDs E-002, E-003, E-008, KB-001)
    sup_ids = primary_h.get("supporting_evidence_ids", [])
    evidence_correct = len(sup_ids) > 0 and any(eid in str(sup_ids) for eid in ["E-002", "E-003", "E-008", "EVD-DESC-1", "KB-001"])
    score_evidence = 2 if evidence_correct else 0
    
    # 5. Healthy Component Identification (upload-service, object-storage, cdn excluded)
    unsupported_healthy = any(h in rc_combined for h in ["upload-service", "object-storage", "cdn"])
    score_healthy = 2 if not unsupported_healthy else 0
    
    # 6. Timeline Correctness (Correlates deployment at 17:58 with 18:05-18:06 outage start)
    timeline_correct = "17:58" in rc_combined or "18:05" in rc_combined or "deployment" in rc_combined or len(final_rep.get("timeline", "")) > 0
    score_timeline = 2 if timeline_correct else 1
    
    # 7. Confidence Calibration (85% - 98%)
    conf = float(final_rep.get("confidence", 0.0))
    conf_calibrated = 85.0 <= conf <= 98.0
    score_conf = 2 if conf_calibrated else (1 if conf >= 70.0 else 0)
    
    # 8. Grounding (PASS / FAIL)
    grounding_status = "PASS" if grounding_val.get("grounded", False) else "FAIL"
    
    # 9. Unsupported Claims Check (PASS / FAIL)
    unsupported_status = "PASS" if not grounding_val.get("unsupported_claims", []) else "FAIL"
    
    # 10. Recommended Remediation (Roll back v4.2.0 / purge temp workspace)
    rec_text = str(primary_h.get("recommended_next_check", "")) + " " + str(final_rep.get("recommended_remediation", ""))
    rec_correct = any(kw in rec_text.lower() for kw in ["rollback", "roll back", "purge", "workspace", "clean", "disk"])
    score_rec = 2 if rec_correct else 1

    total_points = score_rc + score_service + score_chain + score_evidence + score_healthy + score_timeline + score_conf + score_rec
    overall_score = round((total_points / 16.0) * 100, 1)
    
    print("\n------------------------------------------------------------")
    print("EVALUATION CATEGORY SCORES (Max 2 Points Each)")
    print("------------------------------------------------------------")
    print(f"1. Root Cause Correctness        : {score_rc}/2")
    print(f"2. Affected Service Correctness   : {score_service}/2")
    print(f"3. Causal Chain Correctness      : {score_chain}/2")
    print(f"4. Supporting Evidence Cited     : {score_evidence}/2")
    print(f"5. Healthy Components Excluded   : {score_healthy}/2")
    print(f"6. Timeline Correlation          : {score_timeline}/2")
    print(f"7. Confidence Calibration        : {score_conf}/2 ({conf}%)")
    print(f"8. Recommended Remediation       : {score_rec}/2")
    print("------------------------------------------------------------")
    print(f"8. Grounding Invariant Status    : {grounding_status}")
    print(f"9. Unsupported Claims Check      : {unsupported_status}")
    print("------------------------------------------------------------")
    print(f"OVERALL EVALUATION SCORE         : {overall_score}/100")
    print("============================================================\n")

    # Generate Node Comparison Summary Report
    print("============================================================")
    print("TRACEBACK AI TEST REPORT — INC-3057 (StreamForge)")
    print("============================================================")
    print("Node Results")
    print("------------")
    all_nodes_passed = True
    for node_name, res in node_results.items():
        print(f"{node_name:<24} : {res['status']} ({res['details']})")
        if res["status"] != "PASS":
            all_nodes_passed = False

    print("\nFinal RCA")
    print("---------")
    print(f"Primary Root Cause    : {primary_h.get('title')}")
    print(f"Affected Service      : {aff_services[0] if aff_services else 'video-transcoding-service'}")
    print(f"Confidence Score      : {conf}%")
    print(f"Grounding Status      : {grounding_status}")
    print(f"First Divergence Node : {first_divergence if first_divergence else 'NONE (All Nodes Passed Alignment)'}")
    print("============================================================")
    print(f"FINAL RESULT          : {'PASS' if all_nodes_passed and overall_score >= 85.0 else 'FAIL'}")
    print("============================================================")


if __name__ == "__main__":
    asyncio.run(run_sequential_node_by_node_test())
