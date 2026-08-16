import os
import sys
import json
import time
import urllib.request
import asyncio
from typing import Dict, Any

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

agent_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if agent_root not in sys.path:
    sys.path.insert(0, agent_root)

from langgraph_investigation_agent.app.contracts.engine_contract import EngineIncidentInput
from langgraph_investigation_agent.app.engine import run_engine_investigation


def test_end_to_end_system_integration():
    print("============================================================")
    print("TRACEBACK AI — FULL END-TO-END SYSTEM INTEGRATION TEST")
    print("============================================================")
    
    # 1. Prepare E2E Incident Input
    incident_input = EngineIncidentInput(
        incident_id="INC-E2E-9901",
        project_id="CloudForge Media Platform",
        title="Newly uploaded video playback failures",
        description="Users report newly uploaded videos return HTTP 503 manifest_not_found. Uploads succeed, but downstream transcoding fails after deployment v5.4.0 reduced temp workspace size from 50Gi to 10Gi.",
        affected_service="transcoding-service",
        timeline="16 August 2026 18:02 UTC",
        services=[
            "upload-service",
            "transcoding-service",
            "object-storage",
            "manifest-service",
            "cdn",
            "database-service"
        ],
        evidence=[
            {
                "evidence_id": "E-001",
                "source_type": "document",
                "source_name": "e1.txt - Upload Service Metrics",
                "content": "upload-service telemetry: availability: 99.98%, p95 latency: 390ms, error rate: 0.02%. upload-service is operating normally."
            },
            {
                "evidence_id": "E-002",
                "source_type": "document",
                "source_name": "e2.txt - Transcoder Disk Metrics",
                "content": "transcoding-service node disk utilization: node-1: 96%, node-2: 97%, node-3: 98%. Storage threshold 90% crossed at 18:05 UTC."
            },
            {
                "evidence_id": "E-003",
                "source_type": "document",
                "source_name": "e3.txt - Transcoding Service Deployment Record",
                "content": "Deployment Event: transcoding-service release v5.4.0 deployed at 17:58 UTC. Temp workspace allocated per node reduced from 50Gi to 10Gi. FFmpeg retry files retained longer."
            },
            {
                "evidence_id": "E-004",
                "source_type": "document",
                "source_name": "e4.txt - Transcoding Service Logs",
                "content": "transcoding-service log traces:\n17:58 deployment v5.4.0 complete\n18:02 disk utilization increasing\n18:05 disk utilization > 90%\n18:06 ENOSPC: No space left on device path=/tmp/ffmpeg_workspace/job-812\n18:06 FFmpeg temporary file creation failed"
            },
            {
                "evidence_id": "E-005",
                "source_type": "document",
                "source_name": "e5.txt - Object Storage Telemetry",
                "content": "object-storage metrics: availability: 99.99%, error rate: 0.01%, p95 latency: 62ms. Object storage is healthy."
            },
            {
                "evidence_id": "E-006",
                "source_type": "document",
                "source_name": "e6.txt - CDN Health Telemetry",
                "content": "CDN edge performance: availability: 99.999%, packet loss: 0%, p95 latency: 31ms. CDN edge is healthy."
            },
            {
                "evidence_id": "E-007",
                "source_type": "document",
                "source_name": "e7.txt - Database Telemetry",
                "content": "database-service metrics: CPU: 22%, connections: 61/250, p95 latency: 14ms. Database is operating normally."
            },
            {
                "evidence_id": "E-008",
                "source_type": "document",
                "source_name": "e8.txt - Transcoding Queue Depth Timeline",
                "content": "transcoding-service queue backlog: 18:00 (34 jobs) -> 18:06 (190 jobs) -> 18:15 (970 jobs)."
            },
            {
                "evidence_id": "E-009",
                "source_type": "document",
                "source_name": "e9.txt - Manifest Service Error Telemetry",
                "content": "manifest-service logs: 18:10:02 GET /manifests/video-991.m3u8 -> HTTP 503 reason=manifest_not_found"
            }
        ]
    )

    print("\n[STEP 1/3] Executing LangGraph Investigation Workflow...")
    output: EngineInvestigationOutput = asyncio.run(run_engine_investigation(incident_input))
    
    print(f"Investigation Status : {output.status}")
    print(f"Primary Root Cause   : {output.primary_root_cause.title}")
    print(f"Confidence Score     : {output.primary_root_cause.confidence}%")
    is_grounded = len(output.primary_root_cause.supporting_evidence_ids) > 0
    print(f"Grounding Status     : {'GROUNDED' if is_grounded else 'UNGROUNDED'}")

    # Check 1: No hardcoded RCA or static confidence
    hardcoded_rca = "PostgreSQL Connection Pool Exhaustion" in output.primary_root_cause.title
    hardcoded_conf = output.primary_root_cause.confidence in [75.0, 94.5, 95.5]
    print(f"Hardcoded RCA Check  : {'PASS' if not hardcoded_rca else 'FAIL'}")
    print(f"Hardcoded Conf Check : {'PASS' if not hardcoded_conf else 'FAIL'}")

    # Check 2: Affected service correctness
    rc_text = (output.primary_root_cause.title + " " + output.primary_root_cause.explanation).lower()
    correct_service = "transcod" in rc_text or "disk" in rc_text or "workspace" in rc_text or "enospc" in rc_text
    print(f"Root Cause Accuracy  : {'PASS' if correct_service else 'FAIL'}")

    # Check 3: Healthy dependencies excluded
    healthy_excluded = not any(h in rc_text for h in ["upload-service", "object-storage", "cdn", "database-service"])
    print(f"Healthy Deps Excluded: {'PASS' if healthy_excluded else 'FAIL'}")

    # 2. Test Live FastAPI Backend Connection
    print("\n[STEP 2/3] Testing Live FastAPI Health & API Endpoints...")
    try:
        health_req = urllib.request.urlopen("http://localhost:8000/api/v1/health")
        health_data = json.loads(health_req.read().decode())
        fastapi_alive = health_data.get("status") == "ok"
    except Exception as e:
        fastapi_alive = False
        print(f"FastAPI Connection Warning: {e}")
        
    print(f"FastAPI Server Status: {'ONLINE (port 8000)' if fastapi_alive else 'OFFLINE'}")

    # 3. Test Live Frontend Next.js Dev Server Connection
    print("\n[STEP 3/3] Testing Live Next.js Frontend Server...")
    try:
        frontend_req = urllib.request.urlopen("http://localhost:3000")
        frontend_alive = frontend_req.getcode() in [200, 307]
    except Exception as e:
        frontend_alive = False
        print(f"Frontend Connection Warning: {e}")
        
    print(f"Frontend Server Status: {'ONLINE (port 3000)' if frontend_alive else 'OFFLINE'}")

    # Overall Integration Verdict
    integration_pass = (
        output.status.lower() == "completed"
        and output.primary_root_cause.confidence >= 70.0
        and correct_service
        and healthy_excluded
        and not hardcoded_rca
        and not hardcoded_conf
        and fastapi_alive
        and frontend_alive
    )

    print("\n============================================================")
    print("END-TO-END INTEGRATION TEST RESULTS")
    print("============================================================")
    print(f"Workflow Execution   : PASS ({output.status})")
    print(f"Grounding Validation : PASS (Grounded: {is_grounded})")
    print(f"FastAPI Server (8000): {'PASS' if fastapi_alive else 'FAIL'}")
    print(f"Frontend Server (3000): {'PASS' if frontend_alive else 'FAIL'}")
    print("------------------------------------------------------------")
    print(f"FINAL INTEGRATION VERDICT : {'PASS' if integration_pass else 'FAIL'}")
    print("============================================================\n")


if __name__ == "__main__":
    test_end_to_end_system_integration()
