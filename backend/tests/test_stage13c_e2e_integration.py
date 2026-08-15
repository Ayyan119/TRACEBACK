import json
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_stage13c_e2e_log_only():
    """TEST 1: Log only incident investigation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects", json={"name": "E2E Log Only Proj", "slug": "e2e-log-only"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "DB Connection Failure", "description": "Connection pool timeout", "affectedService": "checkout-service"},
        )
        inc_id = inc_res.json()["id"]

        # Log evidence only
        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "log", "title": "app_err.log", "rawContent": "ERROR: max_connections=100 reached"},
        )

        inv_res = await ac.post(f"/api/v1/incidents/{inc_id}/investigate")
        assert inv_res.status_code == 200
        inv_data = inv_res.json()
        assert inv_data["status"] == "Identified"
        assert inv_data["confidence"] > 0.0

        parsed = json.loads(inv_data["rootCauseSummary"])
        assert "investigation_id" in parsed
        assert "selected_hypothesis" in parsed


@pytest.mark.asyncio
async def test_stage13c_e2e_log_and_documents():
    """TEST 2: Log + documents incident investigation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects", json={"name": "E2E Log Doc Proj", "slug": "e2e-log-doc"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Redis Cache Outage", "description": "Memory limit reached", "affectedService": "cart-service"},
        )
        inc_id = inc_res.json()["id"]

        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "log", "title": "redis.log", "rawContent": "OOM command not allowed"},
        )
        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "document", "title": "Redis Architecture PDF", "rawContent": "Redis maxmemory is set to 2GB."},
        )

        inv_res = await ac.post(f"/api/v1/incidents/{inc_id}/investigate")
        assert inv_res.status_code == 200
        inv_data = inv_res.json()
        assert inv_data["status"] == "Identified"


@pytest.mark.asyncio
async def test_stage13c_e2e_log_and_images():
    """TEST 3: Log + images incident investigation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects", json={"name": "E2E Log Img Proj", "slug": "e2e-log-img"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Grafana Latency Spike", "description": "504 Gateway Timeout", "affectedService": "payment-service"},
        )
        inc_id = inc_res.json()["id"]

        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "log", "title": "syslog.log", "rawContent": "504 Gateway Timeout on /checkout"},
        )
        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "image", "title": "Grafana 504 Spike Screenshot", "fileUrl": "https://storage.local/grafana.png"},
        )

        inv_res = await ac.post(f"/api/v1/incidents/{inc_id}/investigate")
        assert inv_res.status_code == 200
        inv_data = inv_res.json()
        assert inv_data["status"] == "Identified"


@pytest.mark.asyncio
async def test_stage13c_e2e_log_documents_and_images():
    """TEST 4: Log + documents + images incident investigation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects", json={"name": "E2E Full Evidence Proj", "slug": "e2e-full-ev"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Cascading Outage Scenario", "description": "Lock contention across services", "affectedService": "checkout-service"},
        )
        inc_id = inc_res.json()["id"]

        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "log", "title": "cluster.log", "rawContent": "DEADLOCK DETECTED on transaction"},
        )
        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "document", "title": "DB Runbook", "rawContent": "Runbook step for clearing locks"},
        )
        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "image", "title": "Architecture Diagram", "fileUrl": "https://storage.local/arch.png"},
        )

        inv_res = await ac.post(f"/api/v1/incidents/{inc_id}/investigate")
        assert inv_res.status_code == 200
        inv_data = inv_res.json()
        assert inv_data["status"] == "Identified"


@pytest.mark.asyncio
async def test_stage13c_e2e_empty_optional_evidence():
    """TEST 5: Incident investigation with empty optional evidence (documents = [], images = [])."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects", json={"name": "E2E Empty Optional", "slug": "e2e-empty-opt"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Empty Optional Evidence Test", "description": "Log only, zero docs or images", "affectedService": "auth-service"},
        )
        inc_id = inc_res.json()["id"]

        # Trigger investigation without creating any document or image evidence
        inv_res = await ac.post(f"/api/v1/incidents/{inc_id}/investigate")
        assert inv_res.status_code == 200
        inv_data = inv_res.json()
        assert inv_data["status"] == "Identified"
