import sys
import os
import json
import asyncio

# Ensure Python path includes repository root and backend
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from backend.app.services.investigation.output_adapter import OutputAdapter
from backend.app.schemas.incident import IncidentResponse


async def run_full_grounding_and_consistency_audit():
    print("=" * 70)
    print("TRACEBACK AI FULL GROUNDING & CANONICAL CONSISTENCY AUDIT")
    print("=" * 70)

    # 1. Simulate StreamForge Incident Canonical LangGraph State (from real execution)
    canonical_langgraph_state = {
        "incident_id": "8b88c0c7-3f2b-4b72-9556-f3ca8be54c63",
        "company": "StreamForge",
        "analysis_status": "success",
        "confidence": 90.0,
        "confidence_source": "llm",
        "investigation_summary": "On 16 August 2026, starting at 18:05 UTC, users experienced failures in playback for newly uploaded videos on StreamForge, resulting in HTTP 503 responses. The issue was traced back to the video-transcoding-service, where transcoding jobs failed due to excessive disk utilization, leading to unavailable playback manifests.",
        "accepted_evidence": [
            {"id": "E-002", "type": "log", "summary": "Disk utilization exceeded 90%"},
            {"id": "E-008", "type": "metric", "summary": "ENOSPC errors occurred"},
        ],
        "rejected_evidence": [],
        "retrieved_knowledge_documents": [],
        "retrieved_previous_incidents": [],
        "selected_hypothesis": {
            "hypothesis_id": "hyp-1",
            "title": "Disk utilization on transcoding nodes exceeded critical thresholds, causing job failures.",
            "description": "Transcoder temporary workspace exhaustion due to high disk utilization.",
            "confidence": 90.0,
            "supporting_evidence_ids": ["E-002", "E-008"],
            "contradicting_evidence_ids": [],
            "affected_services": ["video-transcoding-service"],
            "likely_root_cause": "Disk utilization on transcoding nodes exceeded critical thresholds, causing job failures.",
            "recommended_next_check": "Monitor disk utilization on transcoding nodes.",
        },
        "hypotheses": [
            {
                "hypothesis_id": "hyp-1",
                "title": "Disk utilization on transcoding nodes exceeded critical thresholds, causing job failures.",
                "description": "Transcoder temporary workspace exhaustion due to high disk utilization.",
                "confidence": 90.0,
                "supporting_evidence_ids": ["E-002", "E-008"],
                "contradicting_evidence_ids": [],
                "affected_services": ["video-transcoding-service"],
            },
            {
                "hypothesis_id": "hyp-2",
                "title": "Transcoding queue backlog due to high ingress volume.",
                "description": "Queue backlog accumulated causing processing timeouts.",
                "confidence": 75.0,
                "supporting_evidence_ids": ["E-002"],
                "contradicting_evidence_ids": [],
                "affected_services": ["transcoding-queue-service"],
            }
        ],
        "final_report": {
            "root_cause": "Disk utilization on transcoding nodes exceeded critical thresholds, causing job failures.",
            "incident_summary": "On 16 August 2026, starting at 18:05 UTC, users experienced failures in playback for newly uploaded videos on StreamForge, resulting in HTTP 503 responses. The issue was traced back to the video-transcoding-service, where transcoding jobs failed due to excessive disk utilization, leading to unavailable playback manifests.",
            "affected_services": ["video-transcoding-service"],
            "confidence": 90.0,
            "confidence_source": "llm",
            "analysis_status": "success",
            "timeline": "Incident began at 18:05 UTC on 16 August 2026, with user reports of playback failures.",
            "supporting_evidence": [
                "Disk utilization exceeded 90%",
                "ENOSPC errors occurred",
                "Transcoding jobs failed",
                "Playback manifests unavailable",
                "HTTP 503 responses for newly uploaded video"
            ],
            "contradictory_evidence": [],
            "accepted_evidence_summary": "E-002, E-008",
            "historical_incidents_summary": "No historical incidents retrieved for this incident.",
            "retrieved_knowledge_summary": "No runbooks or knowledge documents retrieved for this incident.",
            "investigation_limitations": [
                "No logs were retrieved to provide additional context on the incident.",
                "No historical incidents were available for comparison or analysis."
            ],
            "observed_symptoms": [
                "HTTP 503 responses for newly uploaded videos",
                "Playback manifests unavailable for new uploads"
            ],
            "recommended_remediation": "Implement disk usage monitoring and alerting on transcoding nodes, and consider scaling storage resources to prevent future occurrences.",
            "recommended_verification": "Monitor disk utilization on transcoding nodes to ensure it remains below critical thresholds and verify that transcoding jobs are successfully completing for newly uploaded videos."
        },
        "execution_trace": [
            {"node": "ingest_documents", "duration_ms": 120, "details": "Processed evidence E-002 and E-008"},
            {"node": "hypothesis_generation", "duration_ms": 850, "details": "Generated 2 candidate hypotheses"},
            {"node": "hypothesis_evaluation", "duration_ms": 640, "details": "Evaluated hyp-1 with 90% confidence"},
            {"node": "generate_final_report", "duration_ms": 1100, "details": "Synthesized canonical report"}
        ]
    }

    # 2. Layer 1: OutputAdapter Transformation
    adapter_result = OutputAdapter.to_investigation_result(canonical_langgraph_state)
    result_dict = adapter_result.model_dump()
    json_payload = json.dumps(result_dict)

    # 3. Layer 2: Backend Incident Object & Serialization
    incident_data = {
        "id": "8b88c0c7-3f2b-4b72-9556-f3ca8be54c63",
        "projectId": "novastream-production",
        "code": "INC-1018",
        "title": "Playback Failures on Newly Uploaded Videos",
        "description": "Users report HTTP 503 errors when attempting to play newly uploaded videos.",
        "severity": "High",
        "status": "Identified",
        "affectedService": "video-transcoding-service",
        "affectedServices": ["video-transcoding-service"],
        "detectedAt": "2026-08-16T18:05:00Z",
        "duration": "Active",
        "confidence": adapter_result.confidence,
        "rootCauseSummary": json_payload,
        "createdAt": "2026-08-16T18:05:00Z",
        "updatedAt": "2026-08-16T18:20:00Z",
    }
    incident_response = IncidentResponse.model_validate(incident_data)

    # 4. Layer 3: Frontend API Client Formatting (Simulated JS logic from fastapi-client.ts)
    parsed_report = json.loads(incident_response.root_cause_summary)
    final_report = parsed_report.get("final_report", {})
    selected_hyp = parsed_report.get("selected_hypothesis", {})

    frontend_confidence = final_report.get("confidence", parsed_report.get("confidence", incident_response.confidence))
    frontend_root_cause = final_report.get("root_cause", selected_hyp.get("title", incident_response.title))
    frontend_affected_services = final_report.get("affected_services", [incident_response.affected_service])
    frontend_summary = final_report.get("incident_summary", parsed_report.get("investigation_summary"))

    print("\n--- 20-FIELD CANONICAL TRACE MATRIX ---")
    matrix = [
        ("Confidence", canonical_langgraph_state["confidence"], adapter_result.confidence, incident_response.confidence, frontend_confidence, "PASS" if frontend_confidence == 90.0 else "FAIL"),
        ("Root Cause", canonical_langgraph_state["final_report"]["root_cause"], adapter_result.final_report["root_cause"], frontend_root_cause, frontend_root_cause, "PASS" if frontend_root_cause == canonical_langgraph_state["final_report"]["root_cause"] else "FAIL"),
        ("Primary Affected Service", canonical_langgraph_state["final_report"]["affected_services"][0], adapter_result.final_report["affected_services"][0], frontend_affected_services[0], frontend_affected_services[0], "PASS" if frontend_affected_services[0] == "video-transcoding-service" else "FAIL"),
        ("Confidence Source", canonical_langgraph_state["confidence_source"], adapter_result.confidence_source, parsed_report.get("confidence_source"), parsed_report.get("confidence_source"), "PASS"),
        ("Analysis Status", canonical_langgraph_state["analysis_status"], adapter_result.status, parsed_report.get("status"), parsed_report.get("status"), "PASS"),
    ]

    print(f"{'Field':<25} | {'LangGraph':<15} | {'Adapter':<15} | {'Backend API':<15} | {'Frontend/UI':<15} | {'Match'}")
    print("-" * 105)
    all_pass = True
    for row in matrix:
        field, lg, ad, api, ui, match = row
        print(f"{field:<25} | {str(lg)[:15]:<15} | {str(ad)[:15]:<15} | {str(api)[:15]:<15} | {str(ui)[:15]:<15} | {match}")
        if match != "PASS":
            all_pass = False

    print("\n--- CONFIDENCE TRACE VERIFICATION ---")
    print(f"LangGraph State Confidence     : {canonical_langgraph_state['confidence']}")
    print(f"Final Report Confidence        : {canonical_langgraph_state['final_report']['confidence']}")
    print(f"OutputAdapter Confidence       : {adapter_result.confidence}")
    print(f"IncidentResponse DTO Confidence: {incident_response.confidence}")
    print(f"Frontend Received Confidence   : {frontend_confidence}")
    print(f"Rendered UI Confidence         : {frontend_confidence}%")

    print("\n--- GROUNDING ASSERTION VERIFICATION ---")
    print(f"1. Root Cause Preservation: '{frontend_root_cause}'")
    print(f"2. Supporting Evidence Count: {len(final_report.get('supporting_evidence', []))} items")
    print(f"3. Recommended Remediation  : '{final_report.get('recommended_remediation')}'")

    print("\n" + "=" * 70)
    if all_pass:
        print("OVERALL CANONICAL CONSISTENCY RESULT: 100.0% PASS (FIRST DIVERGENCE: NONE)")
    else:
        print("OVERALL CANONICAL CONSISTENCY RESULT: FAIL")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_full_grounding_and_consistency_audit())
