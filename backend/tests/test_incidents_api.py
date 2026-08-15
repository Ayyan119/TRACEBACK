import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_incident_success():
    """Test creating an incident via POST /api/v1/projects/{project_id}/incidents."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post(
            "/api/v1/projects",
            json={"name": "ShopFlow Outage", "slug": "shopflow-outage"},
        )
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        inc_payload = {
            "title": "High P95 Latency on Checkout",
            "description": "P95 latency spiked to 3450ms following payment release v2.4.1",
            "severity": "Critical",
            "affectedService": "payment-service",
            "affectedServices": ["payment-service", "order-service"],
            "reporter": "Datadog Alert",
            "environment": "Production",
        }
        res = await ac.post(f"/api/v1/projects/{proj_id}/incidents", json=inc_payload)

    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "High P95 Latency on Checkout"
    assert data["code"] == "INC-1001"
    assert data["severity"] == "Critical"
    assert data["status"] == "Investigating"
    assert data["projectId"] == proj_id
    assert data["affectedService"] == "payment-service"
    assert len(data["affectedServices"]) == 2
    assert "id" in data
    assert "detectedAt" in data
    assert "createdAt" in data


@pytest.mark.asyncio
async def test_get_incidents_by_project_filtering_and_isolation():
    """Test GET /api/v1/projects/{project_id}/incidents listing, filtering, and project data isolation."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        p_a = await ac.post("/api/v1/projects", json={"name": "Proj Inc A", "slug": "proj-inc-a"})
        p_b = await ac.post("/api/v1/projects", json={"name": "Proj Inc B", "slug": "proj-inc-b"})
        id_a = p_a.json()["id"]
        id_b = p_b.json()["id"]

        await ac.post(
            f"/api/v1/projects/{id_a}/incidents",
            json={"title": "Critical DB Lock", "description": "Desc 1", "severity": "Critical"},
        )
        await ac.post(
            f"/api/v1/projects/{id_a}/incidents",
            json={"title": "Low Cache Miss Rate", "description": "Desc 2", "severity": "Low"},
        )
        await ac.post(
            f"/api/v1/projects/{id_b}/incidents",
            json={"title": "Medium Queue Backlog", "description": "Desc 3", "severity": "Medium"},
        )

        res_a = await ac.get(f"/api/v1/projects/{id_a}/incidents")
        assert res_a.status_code == 200
        items_a = res_a.json()
        assert len(items_a) == 2

        res_crit = await ac.get(f"/api/v1/projects/{id_a}/incidents?severity=Critical")
        assert res_crit.status_code == 200
        items_crit = res_crit.json()
        assert len(items_crit) == 1
        assert items_crit[0]["title"] == "Critical DB Lock"

        res_b = await ac.get(f"/api/v1/projects/{id_b}/incidents")
        assert res_b.status_code == 200
        items_b = res_b.json()
        assert len(items_b) == 1
        assert items_b[0]["title"] == "Medium Queue Backlog"


@pytest.mark.asyncio
async def test_get_single_incident_by_id_and_code():
    """Test GET /api/v1/incidents/{incident_id} by UUID, ticket code, and 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "FinBank Incident", "slug": "finbank-inc"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "SWIFT Connector Timeout", "description": "Gateway connection drop"},
        )
        assert inc_res.status_code == 201
        inc_data = inc_res.json()
        incident_id = inc_data["id"]
        ticket_code = inc_data["code"]

        res_by_id = await ac.get(f"/api/v1/incidents/{incident_id}")
        assert res_by_id.status_code == 200
        assert res_by_id.json()["title"] == "SWIFT Connector Timeout"

        res_by_code = await ac.get(f"/api/v1/incidents/{ticket_code}")
        assert res_by_code.status_code == 200
        assert res_by_code.json()["id"] == incident_id

        res_404 = await ac.get("/api/v1/incidents/unknown-incident-id")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_update_incident_status_and_resolution():
    """Test PATCH /api/v1/incidents/{incident_id} updating status to Resolved sets resolvedAt timestamp."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "Patch Proj", "slug": "patch-proj"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Redis Memory Exhaustion", "description": "Cache node OOM kill"},
        )
        assert inc_res.status_code == 201
        inc_id = inc_res.json()["id"]

        patch_payload = {
            "status": "Resolved",
            "rootCauseSummary": "Connection leak in redis client v1.2 resolved by upgrading to v1.3",
            "confidence": 96.0,
        }
        patch_res = await ac.patch(f"/api/v1/incidents/{inc_id}", json=patch_payload)
        assert patch_res.status_code == 200
        data = patch_res.json()
        assert data["status"] == "Resolved"
        assert data["confidence"] == 96.0
        assert "resolvedAt" in data and data["resolvedAt"] is not None
        assert data["rootCauseSummary"] == "Connection leak in redis client v1.2 resolved by upgrading to v1.3"


@pytest.mark.asyncio
async def test_delete_incident_success_and_not_found():
    """Test DELETE /api/v1/incidents/{incident_id} removes incident, decrements project activeIncidentCount, and 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "Del Inc Proj", "slug": "del-inc-proj"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Temp Incident", "description": "Temp description"},
        )
        assert inc_res.status_code == 201
        inc_id = inc_res.json()["id"]

        # Verify activeIncidentCount is 1
        p_check1 = await ac.get(f"/api/v1/projects/{proj_id}")
        assert p_check1.json()["activeIncidentCount"] == 1

        # Delete incident
        del_res = await ac.delete(f"/api/v1/incidents/{inc_id}")
        assert del_res.status_code == 204

        # Verify incident is deleted (404)
        get_res = await ac.get(f"/api/v1/incidents/{inc_id}")
        assert get_res.status_code == 404

        # Verify project activeIncidentCount decremented to 0
        p_check2 = await ac.get(f"/api/v1/projects/{proj_id}")
        assert p_check2.json()["activeIncidentCount"] == 0

        # Delete non-existent incident (404)
        del_404 = await ac.delete("/api/v1/incidents/unknown-incident-id")
        assert del_404.status_code == 404


@pytest.mark.asyncio
async def test_create_incident_non_existent_project():
    """Test creating an incident in a non-existent project returns 404 Not Found."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {"title": "Orphan Outage", "description": "Orphan report"}
        res = await ac.post("/api/v1/projects/unknown-proj-id/incidents", json=payload)

    assert res.status_code == 404
