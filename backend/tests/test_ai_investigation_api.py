import json
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_ai_investigation_flow():
    """Test POST /api/v1/incidents/{incident_id}/investigate triggers AI analysis and populates rootCauseSummary."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create project
        p_res = await ac.post("/api/v1/projects", json={"name": "AI Proj", "slug": "ai-proj"})
        proj_id = p_res.json()["id"]

        # Create incident
        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "High Latency Spike", "description": "Checkout 504 errors", "affectedService": "payment-service"},
        )
        inc_id = inc_res.json()["id"]

        # Attach evidence item
        await ac.post(
            f"/api/v1/incidents/{inc_id}/evidence",
            json={"type": "log", "title": "OOM Error Log", "rawContent": "FATAL: Out of memory"},
        )

        # Trigger AI investigation
        inv_res = await ac.post(f"/api/v1/incidents/{inc_id}/investigate")
        assert inv_res.status_code == 200
        inv_data = inv_res.json()

        assert inv_data["status"] == "Identified"
        assert inv_data["confidence"] > 0.0
        assert "rootCauseSummary" in inv_data and inv_data["rootCauseSummary"] is not None

        # Verify rootCauseSummary is valid InvestigationResult JSON
        parsed_result = json.loads(inv_data["rootCauseSummary"])
        assert "investigation_id" in parsed_result
        assert "confidence" in parsed_result
        assert "selected_hypothesis" in parsed_result or "investigation_summary" in parsed_result
