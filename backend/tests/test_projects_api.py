import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_project_success():
    """Test creating a project via POST /api/v1/projects returns 201 Created."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "name": "ShopFlow E-Commerce",
            "slug": "shopflow-test",
            "description": "Test e-commerce pipeline",
            "environment": "production",
            "ownerTeam": "Checkout Team",
        }
        response = await ac.post("/api/v1/projects", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ShopFlow E-Commerce"
    assert data["slug"] == "shopflow-test"
    assert data["environment"] == "production"
    assert data["serviceCount"] == 0
    assert data["activeIncidentCount"] == 0
    assert "id" in data
    assert "createdAt" in data


@pytest.mark.asyncio
async def test_get_projects_list_and_filtering():
    """Test retrieving list of projects and query filtering via GET /api/v1/projects."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post("/api/v1/projects", json={"name": "Alpha Service", "environment": "production"})
        await ac.post("/api/v1/projects", json={"name": "Beta Staging", "environment": "staging"})

        res_all = await ac.get("/api/v1/projects")
        assert res_all.status_code == 200
        items_all = res_all.json()
        assert len(items_all) == 2

        res_search = await ac.get("/api/v1/projects?search=Alpha")
        assert res_search.status_code == 200
        items_search = res_search.json()
        assert len(items_search) == 1
        assert items_search[0]["name"] == "Alpha Service"

        res_env = await ac.get("/api/v1/projects?environment=staging")
        assert res_env.status_code == 200
        items_env = res_env.json()
        assert len(items_env) == 1
        assert items_env[0]["name"] == "Beta Staging"


@pytest.mark.asyncio
async def test_get_single_project_success_and_not_found():
    """Test GET /api/v1/projects/{project_id} by ID, slug, and non-existent 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        create_res = await ac.post(
            "/api/v1/projects",
            json={"name": "FinBank Core", "slug": "finbank-core", "environment": "production"},
        )
        assert create_res.status_code == 201
        created_data = create_res.json()
        project_id = created_data["id"]

        res_by_id = await ac.get(f"/api/v1/projects/{project_id}")
        assert res_by_id.status_code == 200
        data_by_id = res_by_id.json()
        assert data_by_id["name"] == "FinBank Core"
        assert data_by_id["slug"] == "finbank-core"

        res_by_slug = await ac.get("/api/v1/projects/finbank-core")
        assert res_by_slug.status_code == 200
        data_by_slug = res_by_slug.json()
        assert data_by_slug["id"] == project_id

        res_404 = await ac.get("/api/v1/projects/non-existent-project-id")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_update_project_success_and_not_found():
    """Test PATCH /api/v1/projects/{project_id} partial updates and 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        create_res = await ac.post(
            "/api/v1/projects",
            json={"name": "Old Project Name", "environment": "development"},
        )
        assert create_res.status_code == 201
        created_data = create_res.json()
        project_id = created_data["id"]

        patch_payload = {
            "name": "Updated Project Name",
            "environment": "staging",
            "description": "Updated project description",
        }
        patch_res = await ac.patch(f"/api/v1/projects/{project_id}", json=patch_payload)
        assert patch_res.status_code == 200
        updated_data = patch_res.json()
        assert updated_data["name"] == "Updated Project Name"
        assert updated_data["environment"] == "staging"
        assert updated_data["description"] == "Updated project description"

        patch_404 = await ac.patch("/api/v1/projects/unknown-id", json={"name": "Valid Name"})
        assert patch_404.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_success_and_not_found():
    """Test DELETE /api/v1/projects/{project_id} removes project and 404 handling."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        create_res = await ac.post(
            "/api/v1/projects",
            json={"name": "Project to Delete", "slug": "project-to-delete"},
        )
        assert create_res.status_code == 201
        created_data = create_res.json()
        project_id = created_data["id"]

        # Delete project
        del_res = await ac.delete(f"/api/v1/projects/{project_id}")
        assert del_res.status_code == 204

        # Verify project is gone
        get_res = await ac.get(f"/api/v1/projects/{project_id}")
        assert get_res.status_code == 404

        # Delete non-existent project (404)
        del_404 = await ac.delete("/api/v1/projects/non-existent-id")
        assert del_404.status_code == 404


@pytest.mark.asyncio
async def test_create_project_validation_failure():
    """Test creating a project with missing name returns 422 Unprocessable Entity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "description": "Missing name field",
        }
        response = await ac.post("/api/v1/projects", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_duplicate_slug():
    """Test creating a project with a duplicate slug returns 400 Bad Request."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "name": "FinBank Core",
            "slug": "finbank-unique",
        }
        resp1 = await ac.post("/api/v1/projects", json=payload)
        assert resp1.status_code == 201

        resp2 = await ac.post("/api/v1/projects", json=payload)
        assert resp2.status_code == 400
        err = resp2.json()
        assert "already exists" in err["detail"]
