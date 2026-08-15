import io
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_evidence_crud_flow():
    """Test full Evidence CRUD flow: JSON snippet create, file upload, list, filter, delete."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create project & incident
        p_res = await ac.post("/api/v1/projects", json={"name": "Ev Proj", "slug": "ev-proj"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "High CPU Spike", "description": "CPU at 99%"},
        )
        inc_id = inc_res.json()["id"]

        # 1. Add JSON text snippet evidence
        ev1_res = await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={
                "type": "stack_trace",
                "title": "Exception Trace",
                "source": "Sentry",
                "rawContent": "NullPointerException at PaymentService:142",
            },
        )
        assert ev1_res.status_code == 201
        ev1_data = ev1_res.json()
        assert ev1_data["type"] == "stack_trace"
        assert ev1_data["title"] == "Exception Trace"
        assert ev1_data["incidentId"] == inc_id
        ev1_id = ev1_data["id"]

        # 2. Upload file evidence
        file_content = b"2026-08-14 ERROR Connection pool exhausted"
        file_obj = io.BytesIO(file_content)

        upload_res = await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence/upload",
            data={"title": "Log Dump", "type": "log", "source": "User Upload"},
            files={"file": ("app.log", file_obj, "text/plain")},
        )
        assert upload_res.status_code == 201
        upload_data = upload_res.json()
        assert upload_data["title"] == "Log Dump"
        assert upload_data["mimeType"] == "text/plain"
        assert upload_data["fileSize"] == len(file_content)
        assert "fileUrl" in upload_data

        # 3. List evidence items
        list_res = await ac.get(f"/api/v1/incidents/{inc_id}/evidence")
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) == 2

        # 4. Filter by type
        filter_res = await ac.get(f"/api/v1/incidents/{inc_id}/evidence?type=stack_trace")
        assert filter_res.status_code == 200
        filtered_items = filter_res.json()
        assert len(filtered_items) == 1
        assert filtered_items[0]["title"] == "Exception Trace"

        # 5. Delete evidence item
        del_res = await ac.delete(f"/api/v1/evidence/{ev1_id}")
        assert del_res.status_code == 204

        # Verify deletion
        list_after = await ac.get(f"/api/v1/incidents/{inc_id}/evidence")
        assert len(list_after.json()) == 1
