import io
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_knowledge_crud_flow():
    """Test full Knowledge Base CRUD flow: JSON doc create, file upload, list, filter, delete."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create project
        p_res = await ac.post("/api/v1/projects", json={"name": "KB Proj", "slug": "kb-proj"})
        proj_id = p_res.json()["id"]

        # 1. Add JSON text document
        doc1_res = await ac.post(
            f"/api/v1/projects/{proj_id}/knowledge",
            json={
                "title": "Payment Microservice Runbook",
                "category": "Runbook",
                "content": "# Payment Service Troubleshooting\n\n1. Check Redis cache status.\n2. Restart pod if OOM occurs.",
            },
        )
        assert doc1_res.status_code == 201
        doc1_data = doc1_res.json()
        assert doc1_data["title"] == "Payment Microservice Runbook"
        assert doc1_data["category"] == "Runbook"
        assert doc1_data["projectId"] == proj_id
        doc1_id = doc1_data["id"]

        # 2. Upload file document
        pdf_content = b"%PDF-1.4 Architecture Diagram Spec"
        file_obj = io.BytesIO(pdf_content)

        upload_res = await ac.post(
            f"/api/v1/projects/{proj_id}/knowledge/upload",
            data={"title": "Architecture Topology Spec", "category": "Architecture"},
            files={"file": ("topology.pdf", file_obj, "application/pdf")},
        )
        assert upload_res.status_code == 201
        upload_data = upload_res.json()
        assert upload_data["title"] == "Architecture Topology Spec"
        assert upload_data["category"] == "Architecture"
        assert upload_data["mimeType"] == "application/pdf"
        assert upload_data["fileSize"] == len(pdf_content)

        # 3. List documents
        list_res = await ac.get(f"/api/v1/projects/{proj_id}/knowledge")
        assert list_res.status_code == 200
        items = list_res.json()
        assert len(items) == 2

        # 4. Filter by category
        filter_res = await ac.get(f"/api/v1/projects/{proj_id}/knowledge?category=Runbook")
        assert filter_res.status_code == 200
        filtered = filter_res.json()
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Payment Microservice Runbook"

        # 5. Delete document
        del_res = await ac.delete(f"/api/v1/knowledge/{doc1_id}")
        assert del_res.status_code == 204

        # Verify deletion
        list_after = await ac.get(f"/api/v1/projects/{proj_id}/knowledge")
        assert len(list_after.json()) == 1
