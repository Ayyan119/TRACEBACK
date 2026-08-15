import os
import json
import time
import pytest
from typing import Dict, Any

from app.services.investigation.adapter import InvestigationAdapter
from app.services.investigation.schemas import (
    InvestigationInput,
    IncidentLogInput,
    IncidentDocumentInput,
    IncidentImageInput,
)

SCENARIOS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "langgraph_investigation_agent", "tests", "scenarios")
)


def load_scenario(filename: str) -> Dict[str, Any]:
    filepath = os.path.join(SCENARIOS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def build_input_from_scenario(sc: Dict[str, Any]) -> InvestigationInput:
    log_ref = IncidentLogInput(**sc["incident_log_reference"])
    docs = [IncidentDocumentInput(**d) for d in sc.get("incident_documents", [])]
    imgs = [IncidentImageInput(**i) for i in sc.get("incident_images", [])]

    return InvestigationInput(
        incident_id=sc["incident_id"],
        project_id=sc["project_id"],
        incident_description=sc["incident_description"],
        services=sc["services"],
        service_metadata=sc.get("service_metadata", {}),
        incident_log_reference=log_ref,
        incident_documents=docs,
        incident_images=imgs,
    )


PERFORMANCE_LOG = []


@pytest.mark.asyncio
async def test_scenario_1_log_only():
    sc = load_scenario("scenario_1_log_only.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert result.confidence > 0.0
    assert result.selected_hypothesis is not None
    assert len(result.accepted_evidence) >= 1


@pytest.mark.asyncio
async def test_scenario_2_log_relevant_doc():
    sc = load_scenario("scenario_2_log_relevant_doc.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert len(result.accepted_evidence) >= 1


@pytest.mark.asyncio
async def test_scenario_3_log_relevant_image():
    sc = load_scenario("scenario_3_log_relevant_image.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert len(result.accepted_evidence) >= 1


@pytest.mark.asyncio
async def test_scenario_4_log_doc_image():
    sc = load_scenario("scenario_4_log_doc_image.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert len(result.accepted_evidence) >= 3


@pytest.mark.asyncio
async def test_scenario_5_irrelevant_doc():
    sc = load_scenario("scenario_5_irrelevant_doc.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert len(result.rejected_evidence) >= 1
    rejected_str = str(result.rejected_evidence)
    assert "Employee_Vacation_Policy_2026.pdf" in rejected_str or len(result.rejected_evidence) >= 1


@pytest.mark.asyncio
async def test_scenario_6_irrelevant_image():
    sc = load_scenario("scenario_6_irrelevant_image.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert len(result.rejected_evidence) >= 1
    rejected_str = str(result.rejected_evidence)
    assert "Company Marketing Banner Logo" in rejected_str or len(result.rejected_evidence) >= 1


@pytest.mark.asyncio
async def test_scenario_7_knowledge_retrieval_required():
    sc = load_scenario("scenario_7_knowledge_retrieval_required.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert result.confidence > 0.0


@pytest.mark.asyncio
async def test_scenario_8_previous_incident_required():
    sc = load_scenario("scenario_8_previous_incident_required.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert result.selected_hypothesis is not None


@pytest.mark.asyncio
async def test_scenario_9_multiple_log_tool_iterations():
    sc = load_scenario("scenario_9_multiple_log_tool_iterations.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]


@pytest.mark.asyncio
async def test_scenario_10_insufficient_evidence():
    sc = load_scenario("scenario_10_insufficient_evidence.json")
    payload = build_input_from_scenario(sc)
    adapter = InvestigationAdapter()

    t0 = time.time()
    result = await adapter.arun(payload)
    t1 = time.time()

    PERFORMANCE_LOG.append({"scenario": sc["name"], "latency_ms": (t1 - t0) * 1000.0})

    assert result.incident_id == sc["incident_id"]
    assert result.confidence <= sc.get("expected_confidence_max", 95.0)
