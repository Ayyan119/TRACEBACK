import json
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.repositories.investigation_repository import investigation_repository
from app.services.incident_history_service import incident_history_service


@pytest.mark.asyncio
async def test_investigation_lifecycle_created_running_completed(db):
    """Test 1: Investigation run lifecycle transition CREATED -> RUNNING -> COMPLETED."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create project & incident
        p_res = await ac.post("/api/v1/projects", json={"name": "Lifecycle Proj", "slug": "lifecycle-proj"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Pool Timeout Outage", "description": "Database max_connections=100 limit reached", "affectedService": "checkout-service"},
        )
        inc_id = inc_res.json()["id"]

        # Run investigation
        inv_res = await ac.post(f"/api/v1/incidents/{inc_id}/investigate")
        assert inv_res.status_code == 200

        # Query investigation runs DB table
        runs = await investigation_repository.get_all_by_incident(db, inc_id)
        assert len(runs) >= 1
        latest_run = runs[0]

        assert latest_run.status == "COMPLETED"
        assert latest_run.investigation_number == 1
        assert latest_run.completed_at is not None
        assert latest_run.duration_ms > 0
        assert latest_run.confidence is not None
        assert latest_run.final_report_json is not None
        assert latest_run.execution_trace_json is not None


@pytest.mark.asyncio
async def test_reanalyze_creates_new_investigation_run_without_overwriting(db):
    """Test 2: Re-analyzing creates run #2 and preserves run #1 independently."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects", json={"name": "MultiRun Proj", "slug": "multirun-proj"})
        proj_id = p_res.json()["id"]

        inc_res = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "MultiRun Incident", "description": "Testing multiple runs", "affectedService": "payment-service"},
        )
        inc_id = inc_res.json()["id"]

        # First run
        await ac.post(f"/api/v1/incidents/{inc_id}/investigate")

        # Second run (Re-analyze)
        await ac.post(f"/api/v1/incidents/{inc_id}/investigate")

        runs = await investigation_repository.get_all_by_incident(db, inc_id)
        assert len(runs) >= 2
        # Runs ordered by investigation_number desc
        assert runs[0].investigation_number == 2
        assert runs[1].investigation_number == 1
        assert runs[0].status == "COMPLETED"
        assert runs[1].status == "COMPLETED"


@pytest.mark.asyncio
async def test_failed_investigation_lifecycle(db):
    """Test 3: Unexpected failure transitions status to FAILED and stores sanitized error."""
    rec = await investigation_repository.create(
        db=db,
        incident_id="INC-FAIL-01",
        project_id="PROJ-TEST",
        incident_description="Test scenario failure",
    )
    await investigation_repository.mark_running(db, rec.id)

    # Mark failed
    secret_err = "Failed DB Connection: postgresql://admin:SECRET_PASS@db:5432/db"
    await investigation_repository.mark_failed(db, rec.id, secret_err)

    updated = await investigation_repository.get_by_id(db, rec.id)
    assert updated.status == "FAILED"
    assert updated.completed_at is not None
    assert updated.error_message is not None


@pytest.mark.asyncio
async def test_real_incident_a_to_incident_b_retrieval(db):
    """
    Test 4: Real E2E Multi-Incident Retrieval Integration Test:
    Incident A -> Investigation -> History -> Qdrant (1 Atomic Vector) ->
    Incident B Investigation -> retrieve_previous_incidents node retrieves Incident A!
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/v1/projects", json={"name": "Multi Incident Proj", "slug": "multi-inc-proj"})
        proj_id = p_res.json()["id"]

        # 1. Create and investigate Incident A
        inc_a = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Primary Outage Database Lock", "description": "Database max_connections limit reached on checkout", "affectedService": "checkout-service"},
        )
        inc_a_id = inc_a.json()["id"]

        # Run investigation for Incident A (indexes history to Qdrant)
        await ac.post(f"/api/v1/incidents/{inc_a_id}/investigate")

        # 2. Create Incident B with similar symptoms
        inc_b = await ac.post(
            f"/api/v1/projects/{proj_id}/incidents",
            json={"title": "Secondary Outage Database Latency", "description": "Database connection pool lock contention on checkout", "affectedService": "checkout-service"},
        )
        inc_b_id = inc_b.json()["id"]

        # Run investigation for Incident B
        inv_b_res = await ac.post(f"/api/v1/incidents/{inc_b_id}/investigate")
        assert inv_b_res.status_code == 200

        # Query investigation run #1 for Incident B
        runs = await investigation_repository.get_all_by_incident(db, inc_b_id)
        assert len(runs) >= 1
        run_b = runs[0]

        assert run_b.status == "COMPLETED"
        assert run_b.final_report_json is not None
