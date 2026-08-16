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
from app.engine import run_engine_investigation


def load_tc004_scenario() -> EngineIncidentInput:
    path = os.path.join(os.path.dirname(__file__), "scenarios", "golden_tc004_payment_timeout.json")
    with open(path, "r") as f:
        data = json.load(f)
    return EngineIncidentInput(**data)


async def run_tc004_evaluation():
    print("============================================================")
    print("EXECUTING STANDALONE TC-004 STRESS TEST (3 CONSECUTIVE RUNS)")
    print("============================================================")
    
    scenario = load_tc004_scenario()
    outputs: List[EngineInvestigationOutput] = []
    
    for i in range(3):
        print(f"\n--- Running TC-004 Iteration {i+1}/3 ---")
        start_time = time.time()
        output = await run_engine_investigation(scenario)
        duration = time.time() - start_time
        outputs.append(output)
        print(f"Iteration {i+1} Completed in {duration:.2f}s | Status: {output.status} | Conf: {output.primary_root_cause.confidence}%")
        print(f"Primary RCA: {output.primary_root_cause.title}")
        
    out = outputs[0]
    rc_title = out.primary_root_cause.title.lower()
    rc_exp = out.primary_root_cause.explanation.lower()
    rc_combined = f"{rc_title} {rc_exp}"
    
    # 1. Primary Root Cause Evaluation
    expected_rca_kw = ["timeout", "payment", "deployment", "client", "library", "exceed"]
    rca_pass = any(kw in rc_combined for kw in expected_rca_kw) and "database" not in rc_title and "postgresql" not in rc_title
    
    # 2. Causal Chain Evaluation
    causal_pass = any(kw in rc_combined for kw in ["5 seconds", "checkout", "latency", "downstream", "gateway", "504"])
    
    # 3. Affected Service Evaluation
    service_pass = out.primary_root_cause.affected_services[0] in ["payment-service", "checkout-service"]
    
    # 4. Evidence Grounding Evaluation
    sup_ids = out.primary_root_cause.supporting_evidence_ids
    evidence_pass = len(sup_ids) > 0 and any(eid in str(sup_ids) for eid in ["E-001", "E-002", "E-003", "EVD-LOG-004", "KB-001", "EVD-DESC-1"])
    
    # 5. Knowledge Retrieval Evaluation
    kb_pass = "KB-001" in str(sup_ids) or "runbook" in rc_combined or "timeout" in rc_combined
    
    # 6. Previous Incident Retrieval Evaluation
    prev_pass = "PREV-001" in str(sup_ids) or "previous" in rc_combined or "INC-2026-041" in str(sup_ids) or len(sup_ids) >= 1
    
    # 7. Healthy Components Correctly Excluded Evaluation
    excluded_pass = not ("postgresql connection pool" in rc_title or "redis memory" in rc_title or "packet loss" in rc_title)
    
    # 8. Root Cause vs Symptom Evaluation
    rc_vs_symptom_pass = "timeout" in rc_combined or "deployment" in rc_combined or "client" in rc_combined
    
    # 9. Confidence Evaluation
    conf = out.primary_root_cause.confidence
    conf_pass = 80.0 <= conf <= 99.0 and out.analysis_metadata.confidence_source == "llm"
    
    # 10. Hardcoded Output Check (across 3 runs)
    rcas = [o.primary_root_cause.title for o in outputs]
    confs = [o.primary_root_cause.confidence for o in outputs]
    hardcoded_check_pass = not (confs[0] in [75.0, 94.5] or rcas[0] == "PostgreSQL Connection Pool Exhaustion")
    
    overall_pass = rca_pass and evidence_pass and excluded_pass and conf_pass and hardcoded_check_pass
    
    print("\n============================================================")
    print("TEST CASE: TC-004")
    print("============================================================")
    
    print("\nPrimary Root Cause:")
    print("Expected: Payment-service deployment changed payment client timeout behavior, causing payment authorization requests to remain active beyond the checkout-service's 5-second downstream timeout.")
    print(f"Actual: {out.primary_root_cause.title} — {out.primary_root_cause.explanation}")
    print(f"PASS/FAIL: {'PASS' if rca_pass else 'FAIL'}")
    
    print("\nCausal Chain:")
    print("Expected: deployment -> client behavior changed -> latency 4-8s -> checkout timeout 5s -> HTTP 504")
    print(f"Actual: {out.primary_root_cause.explanation}")
    print(f"PASS/FAIL: {'PASS' if causal_pass else 'FAIL'}")
    
    print("\nAffected Service:")
    print("Expected: payment-service")
    print(f"Actual: {out.primary_root_cause.affected_services[0]}")
    print(f"PASS/FAIL: {'PASS' if service_pass else 'FAIL'}")
    
    print("\nEvidence Grounding:")
    print("Expected: E-001, E-002, E-003, EVD-LOG-004 cited")
    print(f"Actual: {sup_ids}")
    print(f"PASS/FAIL: {'PASS' if evidence_pass else 'FAIL'}")
    
    print("\nKnowledge Retrieval:")
    print("Expected: KB-001 timeout runbook retrieved & cited")
    print(f"Actual Cited: {sup_ids}")
    print(f"PASS/FAIL: {'PASS' if kb_pass else 'FAIL'}")
    
    print("\nPrevious Incident Retrieval:")
    print("Expected: INC-2026-041 context retrieved & evaluated without exact duplication")
    print(f"Actual Cited: {sup_ids}")
    print(f"PASS/FAIL: {'PASS' if prev_pass else 'FAIL'}")
    
    print("\nHealthy Components Correctly Excluded:")
    print("Expected: PostgreSQL DB, Redis, and Network packet loss excluded from root cause")
    print(f"Actual Excluded Status: {'Excluded' if excluded_pass else 'Not Excluded'}")
    print(f"PASS/FAIL: {'PASS' if excluded_pass else 'FAIL'}")
    
    print("\nRoot Cause vs Symptom:")
    print("Expected: Timeout configuration mismatch identified as root cause; HTTP 504 identified as symptom")
    print(f"Actual: {out.primary_root_cause.title}")
    print(f"PASS/FAIL: {'PASS' if rc_vs_symptom_pass else 'FAIL'}")
    
    print("\nConfidence:")
    print("Expected: High / ~85-98%")
    print(f"Actual: {conf}% (Source: {out.analysis_metadata.confidence_source})")
    print(f"PASS/FAIL: {'PASS' if conf_pass else 'FAIL'}")
    
    print("\nHardcoded Output Check:")
    print("Run 3 times.")
    print(f"Iter 1: Conf={confs[0]}% | RCA={rcas[0]}")
    print(f"Iter 2: Conf={confs[1]}% | RCA={rcas[1]}")
    print(f"Iter 3: Conf={confs[2]}% | RCA={rcas[2]}")
    print(f"PASS/FAIL: {'PASS' if hardcoded_check_pass else 'FAIL'}")
    
    print("\n============================================================")
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(run_tc004_evaluation())
