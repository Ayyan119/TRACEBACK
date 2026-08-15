import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_deployment_success():
    """Test creating a deployment event for a service via POST /api/v1/services/{service_id}/deployments."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post(
            "/api/v1/projects",
            json={"name": "ShopFlow Deploy", "slug": "shopflow-deploy"},
        )
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        svc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/services",
            json={"name": "payment-gateway", "type": "Backend"},
        )
        assert svc_res.status_code == 201
        svc_id = svc_res.json()["id"]

        dep_payload = {
            "version": "v2.4.1",
            "commitHash": "7f3a9b2",
            "author": "Alex Rivera",
            "environment": "Production",
            "status": "Success",
            "summary": "Increased connection pool size",
            "configChanges": {"MAX_CONNECTIONS": 50},
            "diffSummary": "+12 -3 lines",
            "prUrl": "https://github.com/shopflow/payment-gateway/pull/42",
        }
        res = await ac.post(f"/api/v1/services/{svc_id}/deployments", json=dep_payload)

    assert res.status_code == 201
    data = res.json()
    assert data["version"] == "v2.4.1"
    assert data["commitHash"] == "7f3a9b2"
    assert data["author"] == "Alex Rivera"
    assert data["serviceId"] == svc_id
    assert data["projectId"] == proj_id
    assert data["status"] == "Success"
    assert "id" in data
    assert "deployedAt" in data
    assert "createdAt" in data


@pytest.mark.asyncio
async def test_get_deployments_by_service_success_and_not_found():
    """Test GET /api/v1/services/{service_id}/deployments history listing and 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "FinBank Deploy", "slug": "finbank-deploy"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        svc_res = await ac.post(f"/api/v1/projects/{proj_id}/services", json={"name": "treasury-api"})
        assert svc_res.status_code == 201
        svc_id = svc_res.json()["id"]

        await ac.post(f"/api/v1/services/{svc_id}/deployments", json={"version": "v1.0.0", "author": "dev-1"})
        await ac.post(f"/api/v1/services/{svc_id}/deployments", json={"version": "v1.0.1", "author": "dev-2"})

        res = await ac.get(f"/api/v1/services/{svc_id}/deployments")
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 2
        assert items[0]["version"] == "v1.0.1"
        assert items[1]["version"] == "v1.0.0"

        res_404 = await ac.get("/api/v1/services/unknown-service-id/deployments")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_get_deployments_by_project_timeline_and_isolation():
    """Test GET /api/v1/projects/{project_id}/deployments aggregates all service releases in project."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create Project A & Project B
        p_a = await ac.post("/api/v1/projects", json={"name": "Proj Timeline A", "slug": "proj-time-a"})
        p_b = await ac.post("/api/v1/projects", json={"name": "Proj Timeline B", "slug": "proj-time-b"})
        id_a = p_a.json()["id"]
        id_b = p_b.json()["id"]

        # Services in Proj A
        s_a1 = await ac.post(f"/api/v1/projects/{id_a}/services", json={"name": "service-a1"})
        s_a2 = await ac.post(f"/api/v1/projects/{id_a}/services", json={"name": "service-a2"})
        # Service in Proj B
        s_b1 = await ac.post(f"/api/v1/projects/{id_b}/services", json={"name": "service-b1"})

        # Deployments in Proj A
        await ac.post(f"/api/v1/services/{s_a1.json()['id']}/deployments", json={"version": "v1.0"})
        await ac.post(f"/api/v1/services/{s_a2.json()['id']}/deployments", json={"version": "v2.0"})

        # Deployment in Proj B
        await ac.post(f"/api/v1/services/{s_b1.json()['id']}/deployments", json={"version": "v3.0"})

        # Fetch timeline for Proj A
        res_a = await ac.get(f"/api/v1/projects/{id_a}/deployments")
        assert res_a.status_code == 200
        items_a = res_a.json()
        assert len(items_a) == 2

        # Fetch timeline for Proj B
        res_b = await ac.get(f"/api/v1/projects/{id_b}/deployments")
        assert res_b.status_code == 200
        items_b = res_b.json()
        assert len(items_b) == 1
        assert items_b[0]["version"] == "v3.0"

        # Fetch for non-existent project (404)
        res_404 = await ac.get("/api/v1/projects/unknown-proj-id/deployments")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_create_deployment_non_existent_service():
    """Test creating a deployment for a non-existent service returns 404 Not Found."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        dep_payload = {"version": "v1.0.0", "author": "ci-bot"}
        res = await ac.post("/api/v1/services/unknown-service-id/deployments", json=dep_payload)

    assert res.status_code == 404
