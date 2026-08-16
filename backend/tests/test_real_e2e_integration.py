import os
import sys
import json
import asyncio
import httpx

API_BASE = "http://localhost:8000/api/v1"

async def test_full_real_e2e_flow():
    print("============================================================")
    print("STARTING REAL END-TO-END SYSTEM VALIDATION (API -> LANGGRAPH -> DB)")
    print("============================================================")
    
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        # 1. Health check
        res = await client.get(f"{API_BASE}/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("✓ Health Check Passed: FastAPI Backend active")
        
        # 2. Get or Create Project
        res = await client.get(f"{API_BASE}/projects")
        if res.status_code != 200 or not res.json():
            print(f"No existing project found ({res.status_code}: {res.text}), creating new test project...")
            res = await client.post(f"{API_BASE}/projects", json={"name": "E2E Test Project", "slug": "e2e-project"})
            assert res.status_code == 201, f"Create project failed: {res.text}"
            proj_id = res.json()["id"]
        else:
            projects = res.json()
            proj_id = projects[0]["id"]
        print(f"✓ Using Active Project ID: {proj_id}")
        
        # 3. Create real incident
        inc_payload = {
            "title": "E2E Validation Incident — High Checkout Latency",
            "description": "Customers reporting stuck orders and HTTP 504 errors on checkout-service during peak load. Database CPU 48%, connections 61/100, Redis evictions 0. Payment service authorization latency 4200ms.",
            "severity": "Critical",
            "affected_service": "checkout-service"
        }
        res = await client.post(f"{API_BASE}/projects/{proj_id}/incidents", json=inc_payload)
        assert res.status_code == 201, f"Create incident failed: {res.text}"
        inc_data = res.json()
        inc_id = inc_data["id"]
        print(f"✓ Created Real Incident ID: {inc_id}")
        
        # 4. Upload mandatory log file
        log_content = (
            "2026-07-26T14:08:41Z INFO payment-service deployment version=2026.07.26-3 status=SUCCESS\n"
            "2026-07-26T14:10:14Z WARN payment-service latency_ms=4200 endpoint=/payments/authorize\n"
            "2026-07-26T14:10:23Z ERROR api-gateway request_id=chk-11291 status=504 upstream=checkout-service\n"
            "2026-07-26T14:13:02Z INFO postgresql-db cpu_percent=48 connections=61 max_connections=100\n"
            "2026-07-26T14:13:05Z INFO redis-cache memory_percent=52 evictions=0\n"
        )
        files = {"file": ("mandatory_system.log", log_content.encode("utf-8"), "text/plain")}
        data = {"type": "log", "title": "Mandatory System Log", "source": "E2E Suite", "is_mandatory_log": "true"}
        res = await client.post(f"{API_BASE}/incidents/{inc_id}/evidence/upload", data=data, files=files)
        assert res.status_code == 201, f"Upload mandatory log failed: {res.text}"
        print("✓ Uploaded Mandatory Log File")
        
        # 5. Trigger Real AI Investigation
        print(f"🚀 Triggering Real AI Investigation for incident {inc_id}...")
        start_t = asyncio.get_event_loop().time()
        res = await client.post(f"{API_BASE}/incidents/{inc_id}/investigate")
        duration = asyncio.get_event_loop().time() - start_t
        assert res.status_code == 200, f"Investigation failed: {res.text}"
        inv_data = res.json()
        
        print(f"✓ Investigation Finished in {duration:.2f}s | Status: {inv_data.get('status')}")
        selected_hyp = inv_data.get('selected_hypothesis') or {}
        print(f"   Primary Root Cause: {selected_hyp.get('title')}")
        print(f"   Confidence: {inv_data.get('confidence')}%")
        print(f"   Confidence Source: {inv_data.get('confidence_source')}")
        
        # 6. Verify DB Persistence & History Fetch
        res = await client.get(f"{API_BASE}/incidents/{inc_id}/investigations")
        assert res.status_code == 200
        runs = res.json()
        assert len(runs) >= 1
        print(f"✓ Verified Database Persistence: {len(runs)} investigation run(s) saved in DB")
        
        print("\n============================================================")
        print("REAL E2E FLOW VALIDATION: ALL STAGES SUCCESSFUL")
        print("============================================================")

if __name__ == "__main__":
    asyncio.run(test_full_real_e2e_flow())
