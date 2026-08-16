import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

import sys
import os

agent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
import app
backend_app_dir = os.path.join(backend_dir, "app")
if backend_app_dir not in app.__path__:
    app.__path__.append(backend_app_dir)

import app.models
backend_models_dir = os.path.join(backend_dir, "app", "models")
if backend_models_dir not in app.models.__path__:
    app.models.__path__.append(backend_models_dir)

from app.models.llm_invoker import invoke_llm_with_orchestration
from app.analysis.hypotheses import generate_ranked_hypotheses
from app.graph.nodes import generate_hypotheses_node, generate_final_report_node, initialize_state_node
from app.services.investigation.output_adapter import OutputAdapter


@pytest.mark.asyncio
async def test_llm_invoker_retry_on_503():
    """TEST 4: Gemini 503 triggers controlled retry/backoff."""
    mock_fn = AsyncMock(side_effect=[
        Exception("503 Service Unavailable"),
        Exception("503 Service Unavailable"),
        "success_response"
    ])
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        res = await invoke_llm_with_orchestration(mock_fn, provider_name="gemini", node_name="test_node")
        assert res == "success_response"
        assert mock_fn.call_count == 3
        assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_llm_invoker_retry_on_429():
    """TEST 5: Gemini 429 triggers controlled retry/backoff."""
    mock_fn = AsyncMock(side_effect=[
        Exception("429 RESOURCE_EXHAUSTED"),
        "success_response"
    ])
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        res = await invoke_llm_with_orchestration(mock_fn, provider_name="gemini", node_name="test_node")
        assert res == "success_response"
        assert mock_fn.call_count == 2
        assert mock_sleep.call_count == 1


@pytest.mark.asyncio
async def test_llm_failure_does_not_produce_fake_75_confidence():
    """TEST 6: LLM failure does NOT produce fake 75% confidence."""
    evidence_analysis = {
        "affected_service": "payment-api",
        "what_happened": "Timeout error spiking latency",
        "symptoms": ["HTTP 504 Gateway Timeout"],
    }
    accepted_evidence = [{"evidence_id": "EVD-1", "source_name": "Error Log"}]
    
    with patch("app.analysis.hypotheses.safe_invoke_structured_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = None  # Simulate LLM failure
        ranking, is_fallback = await generate_ranked_hypotheses(evidence_analysis, accepted_evidence)
        
        assert is_fallback is True
        assert ranking.hypotheses[0].confidence == 0.0
        assert ranking.hypotheses[0].confidence != 75.0


@pytest.mark.asyncio
async def test_llm_failure_does_not_produce_hardcoded_rca():
    """TEST 7: LLM failure does NOT produce hardcoded PostgreSQL RCA."""
    evidence_analysis = {
        "affected_service": "auth-service",
        "what_happened": "JWT signing key mismatch error",
        "symptoms": ["HTTP 401 Unauthorized"],
    }
    accepted_evidence = [{"evidence_id": "EVD-AUTH-1", "source_name": "Auth Log"}]
    
    with patch("app.analysis.hypotheses.safe_invoke_structured_llm", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = None
        ranking, is_fallback = await generate_ranked_hypotheses(evidence_analysis, accepted_evidence)
        
        root_cause = ranking.hypotheses[0].likely_root_cause
        assert "JWT signing key mismatch error" in root_cause
        assert "PostgreSQL Connection Pool Exhaustion" not in root_cause
        assert "customer_id" not in root_cause


@pytest.mark.asyncio
async def test_degraded_status_in_output_adapter():
    """TEST 8: OutputAdapter correctly marks DEGRADED status when confidence_source is fallback."""
    state = {
        "incident_id": "INC-8888",
        "investigation_id": "inv-8888",
        "confidence": 0.0,
        "confidence_source": "fallback",
        "analysis_status": "degraded",
        "failed_llm_nodes": ["generate_hypotheses"],
        "investigation_summary": "Degraded analysis completed using fallback.",
        "accepted_evidence": [],
    }
    
    result = OutputAdapter.to_investigation_result(state)
    assert result.status == "DEGRADED"
    assert result.confidence == 0.0
    assert result.confidence_source == "fallback"
    assert result.analysis_status == "degraded"
    assert result.failed_llm_nodes == ["generate_hypotheses"]
