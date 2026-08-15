import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_service_success():
    """Test creating a service in a project via POST /api/v1/projects/{project_id}/services."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post(
            "/api/v1/projects",
            json={"name": "ShopFlow Checkout", "slug": "shopflow-services"},
        )
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        service_payload = {
            "name": "payment-service",
            "type": "Backend",
            "description": "Processes payment transactions",
            "ownerTeam": "Payments Team",
            "dependencies": [{"id": "postgres", "name": "postgres", "type": "database"}],
        }
        res = await ac.post(f"/api/v1/projects/{proj_id}/services", json=service_payload)

    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "payment-service"
    assert data["projectId"] == proj_id
    assert data["health"] == "Healthy"
    assert data["latencyMs"] == 15.0
    assert data["errorRatePercent"] == 0.0
    assert len(data["dependencies"]) == 1
    assert "id" in data
    assert "createdAt" in data


@pytest.mark.asyncio
async def test_get_services_by_project_isolation():
    """Test GET /api/v1/projects/{project_id}/services respects strict project data isolation."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        p_a = await ac.post("/api/v1/projects", json={"name": "Project Alpha", "slug": "proj-a"})
        p_b = await ac.post("/api/v1/projects", json={"name": "Project Beta", "slug": "proj-b"})
        id_a = p_a.json()["id"]
        id_b = p_b.json()["id"]

        await ac.post(f"/api/v1/projects/{id_a}/services", json={"name": "alpha-service"})
        await ac.post(f"/api/v1/projects/{id_b}/services", json={"name": "beta-service"})

        res_a = await ac.get(f"/api/v1/projects/{id_a}/services")
        assert res_a.status_code == 200
        services_a = res_a.json()
        assert len(services_a) == 1
        assert services_a[0]["name"] == "alpha-service"

        res_b = await ac.get(f"/api/v1/projects/{id_b}/services")
        assert res_b.status_code == 200
        services_b = res_b.json()
        assert len(services_b) == 1
        assert services_b[0]["name"] == "beta-service"


@pytest.mark.asyncio
async def test_get_single_service_by_id_and_name():
    """Test GET /api/v1/services/{service_id} by UUID, name, and 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "ShopFlow Order", "slug": "shopflow-order"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        svc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/services",
            json={"name": "inventory-service", "type": "Worker"},
        )
        assert svc_res.status_code == 201
        svc_data = svc_res.json()
        service_id = svc_data["id"]

        res_by_id = await ac.get(f"/api/v1/services/{service_id}")
        assert res_by_id.status_code == 200
        assert res_by_id.json()["name"] == "inventory-service"

        res_by_name = await ac.get("/api/v1/services/inventory-service")
        assert res_by_name.status_code == 200
        assert res_by_name.json()["id"] == service_id

        res_404 = await ac.get("/api/v1/services/unknown-service-id")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_update_service_success_and_not_found():
    """Test PATCH /api/v1/services/{service_id} metric/health updates and 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "ShopFlow Patch", "slug": "shopflow-patch"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        create_svc = await ac.post(
            f"/api/v1/projects/{proj_id}/services",
            json={"name": "auth-service", "type": "Backend"},
        )
        assert create_svc.status_code == 201
        svc_id = create_svc.json()["id"]

        patch_payload = {
            "health": "Degraded",
            "latencyMs": 3450.0,
            "errorRatePercent": 14.2,
            "ownerTeam": "Security Team",
        }
        patch_res = await ac.patch(f"/api/v1/services/{svc_id}", json=patch_payload)
        assert patch_res.status_code == 200
        updated_data = patch_res.json()
        assert updated_data["health"] == "Degraded"
        assert updated_data["latencyMs"] == 3450.0
        assert updated_data["errorRatePercent"] == 14.2
        assert updated_data["ownerTeam"] == "Security Team"

        patch_404 = await ac.patch("/api/v1/services/unknown-service", json={"health": "Healthy"})
        assert patch_404.status_code == 404


@pytest.mark.asyncio
async def test_delete_service_success_and_not_found():
    """Test DELETE /api/v1/services/{service_id} removes service, decrements project service_count, and handles 404."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "Del Proj", "slug": "del-proj"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        svc_res = await ac.post(f"/api/v1/projects/{proj_id}/services", json={"name": "temp-service"})
        assert svc_res.status_code == 201
        svc_id = svc_res.json()["id"]

        # Check project serviceCount is 1
        p_check1 = await ac.get(f"/api/v1/projects/{proj_id}")
        assert p_check1.json()["serviceCount"] == 1

        # Delete service
        del_res = await ac.delete(f"/api/v1/services/{svc_id}")
        assert del_res.status_code == 204

        # Verify service is deleted
        get_res = await ac.get(f"/api/v1/services/{svc_id}")
        assert get_res.status_code == 404

        # Check project serviceCount decremented to 0
        p_check2 = await ac.get(f"/api/v1/projects/{proj_id}")
        assert p_check2.json()["serviceCount"] == 0

        # Delete non-existent service (404)
        del_404 = await ac.delete("/api/v1/services/unknown-service-id")
        assert del_404.status_code == 404


@pytest.mark.asyncio
async def test_create_service_non_existent_project():
    """Test creating a service in a non-existent project returns 404 Not Found."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {"name": "orphan-service"}
        res = await ac.post("/api/v1/projects/non-existent-project/services", json=payload)

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_service_duplicate_name():
    """Test creating a duplicate service name in the same project returns 400 Bad Request."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        proj_res = await ac.post("/api/v1/projects", json={"name": "FinBank App", "slug": "finbank-app"})
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        payload = {"name": "ledger-api"}
        resp1 = await ac.post(f"/api/v1/projects/{proj_id}/services", json=payload)
        assert resp1.status_code == 201

        resp2 = await ac.post(f"/api/v1/projects/{proj_id}/services", json=payload)
        assert resp2.status_code == 400
        err = resp2.json()
        assert "already exists" in err["detail"]
