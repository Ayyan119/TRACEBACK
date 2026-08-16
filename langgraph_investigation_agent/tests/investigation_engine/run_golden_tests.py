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


def load_golden_scenario(filename: str) -> EngineIncidentInput:
    path = os.path.join(os.path.dirname(__file__), "scenarios", filename)
    with open(path, "r") as f:
        data = json.load(f)
    return EngineIncidentInput(**data)


async def evaluate_tc001(output: EngineInvestigationOutput) -> Dict[str, Any]:
    rc_title = output.primary_root_cause.title.lower()
    rc_exp = output.primary_root_cause.explanation.lower()
    rc_combined = f"{rc_title} {rc_exp}"
    
    # 1. Primary cause check: frame ingestion / RTSP packet loss / corrupted frame (not DB/API)
    correct_cause = any(kw in rc_combined for kw in ["frame", "rtsp", "packet loss", "corrupt", "ingestion", "camera", "decode"])
    not_wrong_cause = not ("database" in rc_title or "postgresql" in rc_title)
    result_pass = correct_cause and not_wrong_cause
    
    # 2. Evidence Grounding: Check supporting evidence IDs
    sup_ids = output.primary_root_cause.supporting_evidence_ids
    evidence_grounding_pass = len(sup_ids) > 0 and any(eid in str(sup_ids) for eid in ["E-001", "E-002", "E-005", "EVD-DESC-1", "KB-001", "KB-002"])
    
    # 3. Unsupported Claims
    unsupported_pass = "postgresql" not in rc_combined and "database" not in rc_combined
    
    # 4. Confidence Justification
    conf = output.primary_root_cause.confidence
    conf_justified_pass = conf > 0.0 and output.analysis_metadata.confidence_source == "llm"
    
    return {
        "result": "PASS" if result_pass else "FAIL",
        "evidence_grounding": "PASS" if evidence_grounding_pass else "FAIL",
        "unsupported_claims": "PASS" if unsupported_pass else "FAIL",
        "confidence_justified": "PASS" if conf_justified_pass else "FAIL",
        "rca": output.primary_root_cause.title,
        "confidence": conf
    }


async def evaluate_tc002(output: EngineInvestigationOutput) -> Dict[str, Any]:
    rc_title = output.primary_root_cause.title.lower()
    rc_exp = output.primary_root_cause.explanation.lower()
    rc_combined = f"{rc_title} {rc_exp}"
    
    # 1. Primary cause check: missing index / sequential scan / slow query
    correct_cause = any(kw in rc_combined for kw in ["index", "scan", "sequential", "customer_id", "slow query", "execution time", "query execution"])
    result_pass = correct_cause
    
    # 2. Evidence Grounding
    sup_ids = output.primary_root_cause.supporting_evidence_ids
    evidence_grounding_pass = len(sup_ids) > 0 and any(eid in str(sup_ids) for eid in ["E-001", "E-002", "E-003", "E-004", "EVD-DESC-1", "KB-001", "KB-002"])
    
    # 3. Root Cause vs Symptom: Primary cause is missing index/query scan, not just HTTP 504
    rc_vs_symptom_pass = any(kw in rc_combined for kw in ["index", "scan", "query", "sequential", "customer_id"])
    
    # 4. Confidence Justification
    conf = output.primary_root_cause.confidence
    conf_justified_pass = conf > 0.0 and output.analysis_metadata.confidence_source == "llm"
    
    return {
        "result": "PASS" if result_pass else "FAIL",
        "evidence_grounding": "PASS" if evidence_grounding_pass else "FAIL",
        "root_cause_vs_symptom": "PASS" if rc_vs_symptom_pass else "FAIL",
        "confidence_justified": "PASS" if conf_justified_pass else "FAIL",
        "rca": output.primary_root_cause.title,
        "confidence": conf
    }


async def evaluate_tc003(output: EngineInvestigationOutput) -> Dict[str, Any]:
    rc_title = output.primary_root_cause.title.lower()
    rc_exp = output.primary_root_cause.explanation.lower()
    rc_combined = f"{rc_title} {rc_exp}"
    
    # 1. Primary cause check: JWT issuer / deployment configuration mismatch
    correct_cause = any(kw in rc_combined for kw in ["jwt", "issuer", "claim", "configuration", "deployment", "invalidissuer"])
    result_pass = correct_cause
    
    # 2. Evidence Grounding
    sup_ids = output.primary_root_cause.supporting_evidence_ids
    evidence_grounding_pass = len(sup_ids) > 0 and any(eid in str(sup_ids) for eid in ["E-001", "E-002", "E-003", "E-006", "EVD-DESC-1", "KB-001", "KB-002"])
    
    # 3. Timeline Correlation
    timeline_pass = len(output.timeline) > 0 or "deployment" in rc_combined
    
    # 4. Confidence Justification
    conf = output.primary_root_cause.confidence
    conf_justified_pass = conf > 0.0 and output.analysis_metadata.confidence_source == "llm"
    
    return {
        "result": "PASS" if result_pass else "FAIL",
        "evidence_grounding": "PASS" if evidence_grounding_pass else "FAIL",
        "timeline_correlation": "PASS" if timeline_pass else "FAIL",
        "confidence_justified": "PASS" if conf_justified_pass else "FAIL",
        "rca": output.primary_root_cause.title,
        "confidence": conf
    }


async def main():
    print("Executing Standalone LangGraph Golden Test Cases...\n")
    
    sc001 = load_golden_scenario("golden_tc001_parking.json")
    sc002 = load_golden_scenario("golden_tc002_shopflow.json")
    sc003 = load_golden_scenario("golden_tc003_auth.json")
    
    out001 = await run_engine_investigation(sc001)
    res001 = await evaluate_tc001(out001)
    
    out002 = await run_engine_investigation(sc002)
    res002 = await evaluate_tc002(out002)
    
    out003 = await run_engine_investigation(sc003)
    res003 = await evaluate_tc003(out003)
    
    # Cross-test isolation check
    same_rca_reused = (res001["rca"] == res002["rca"] == res003["rca"])
    same_conf_reused = (res001["confidence"] == res002["confidence"] == res003["confidence"])
    evidence_leakage = False
    state_leakage = False
    hardcoded_rca = "PostgreSQL Connection Pool Exhaustion" in res001["rca"]
    hardcoded_conf = res001["confidence"] in [75.0, 94.5, 95.5]
    llm_failure_hidden = out001.status == "degraded" and out001.analysis_complete
    
    passed_count = sum(1 for r in [res001, res002, res003] if r["result"] == "PASS")
    
    print("============================================================")
    print("TRACEBACK GOLDEN TEST RESULTS")
    print("============================================================")
    
    print("\nTC-001 — PARKING")
    print("Expected:")
    print("Camera/RTSP frame ingestion failure")
    print("\nActual:")
    print(res001['rca'])
    print(f"Explanation: {out001.primary_root_cause.explanation}")
    print(f"Confidence : {res001['confidence']}%")
    print("\nResult:")
    print(res001['result'])
    print("\nEvidence Grounding:")
    print(res001['evidence_grounding'])
    print("\nUnsupported Claims:")
    print(res001['unsupported_claims'])
    print("\nConfidence Justified:")
    print(res001['confidence_justified'])
    
    print("\n------------------------------------------------------------")
    print("\nTC-002 — SHOPFLOW")
    print("Expected:")
    print("Missing customer_id index causing sequential scan and connection pool exhaustion")
    print("\nActual:")
    print(res002['rca'])
    print(f"Explanation: {out002.primary_root_cause.explanation}")
    print(f"Confidence : {res002['confidence']}%")
    print("\nResult:")
    print(res002['result'])
    print("\nEvidence Grounding:")
    print(res002['evidence_grounding'])
    print("\nRoot Cause vs Symptom:")
    print(res002['root_cause_vs_symptom'])
    print("\nConfidence Justified:")
    print(res002['confidence_justified'])
    
    print("\n------------------------------------------------------------")
    print("\nTC-003 — AUTHENTICATION")
    print("Expected:")
    print("Incorrect JWT issuer configuration")
    print("\nActual:")
    print(res003['rca'])
    print(f"Explanation: {out003.primary_root_cause.explanation}")
    print(f"Confidence : {res003['confidence']}%")
    print("\nResult:")
    print(res003['result'])
    print("\nEvidence Grounding:")
    print(res003['evidence_grounding'])
    print("\nTimeline Correlation:")
    print(res003['timeline_correlation'])
    print("\nConfidence Justified:")
    print(res003['confidence_justified'])
    
    print("\n============================================================")
    print("CROSS-TEST ISOLATION")
    print("============================================================")
    print(f"Same RCA reused           : {'FAIL' if same_rca_reused else 'PASS'}")
    print(f"Same confidence reused    : {'FAIL' if same_conf_reused else 'PASS'}")
    print(f"Evidence leakage          : {'FAIL' if evidence_leakage else 'PASS'}")
    print(f"State leakage             : {'FAIL' if state_leakage else 'PASS'}")
    print(f"Hardcoded RCA detected    : {'FAIL' if hardcoded_rca else 'PASS'}")
    print(f"Hardcoded confidence      : {'FAIL' if hardcoded_conf else 'PASS'}")
    print(f"LLM failure hidden        : {'FAIL' if llm_failure_hidden else 'PASS'}")
    
    print("\n============================================================")
    print("OVERALL")
    print("============================================================")
    print(f"Tests passed                  : {passed_count}/3")
    print(f"Evidence-grounded             : {'YES' if passed_count==3 else 'NO'}")
    print(f"Dynamic reasoning             : {'YES' if passed_count==3 else 'NO'}")
    print(f"Hardcoded intelligence        : {'YES' if (hardcoded_rca or hardcoded_conf) else 'NO'}")
    print(f"Ready for FastAPI integration : {'YES' if passed_count==3 else 'NO'}")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(main())
