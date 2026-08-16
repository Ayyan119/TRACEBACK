import time
import logging
from typing import Dict, Any, List

from langgraph_investigation_agent.app.contracts.engine_contract import (
    EngineIncidentInput,
    EngineInvestigationOutput,
    PrimaryRootCause,
    AlternativeHypothesis,
    RecommendedAction,
    AnalysisMetadata,
)
from langgraph_investigation_agent.app.graph.workflow import build_investigation_graph
from langgraph_investigation_agent.app.graph.state import InvestigationState

logger = logging.getLogger("langgraph_agent.engine")


async def run_engine_investigation(input_data: EngineIncidentInput) -> EngineInvestigationOutput:
    """
    Executes the standalone LangGraph AI Investigation Engine.
    Operates 100% independently of FastAPI routes, PostgreSQL database tables, or Frontend state.
    """
    start_time = time.time()
    
    # 1. Map EngineIncidentInput to InvestigationState
    accepted_evidence: List[Dict[str, Any]] = []
    
    # Add mandatory description evidence
    accepted_evidence.append({
        "evidence_id": "EVD-DESC-1",
        "source_type": "description",
        "source_name": "Incident Description",
        "content": f"{input_data.title}. {input_data.description}",
        "relevance": True,
        "confidence": 1.0,
    })
    
    # Add input evidence items
    for item in input_data.evidence:
        accepted_evidence.append({
            "evidence_id": item.evidence_id,
            "source_type": item.source_type,
            "source_name": item.source_name,
            "content": item.content,
            "relevance": True,
            "confidence": 1.0,
            "metadata": item.metadata,
        })
        
    initial_state: InvestigationState = {
        "investigation_id": f"engine-inv-{int(time.time()*1000)}",
        "incident_id": input_data.incident_id,
        "project_id": input_data.project_id,
        "incident_description": f"{input_data.title}. {input_data.description}",
        "services": [input_data.affected_service],
        "accepted_evidence": accepted_evidence,
        "processed_document_evidence": [],
        "processed_image_evidence": [],
        "rejected_evidence": [],
        "log_query_history": [],
        "retrieved_logs": [],
        "tool_iterations": 0,
        "investigation_iterations": 0,
        "retrieval_required": False,
        "retrieved_knowledge_documents": [],
        "retrieved_previous_incidents": [],
        "reranked_documents": [],
        "confidence_source": "llm",
        "analysis_status": "success",
        "failed_llm_nodes": [],
        "errors": [],
        "warnings": [],
        "execution_trace": [],
    }

    # 2. Build and execute graph
    graph = build_investigation_graph()
    final_state = await graph.ainvoke(initial_state)
    
    exec_duration = time.time() - start_time
    
    # 3. Extract final outputs from state
    final_report = final_state.get("final_report", {}) or {}
    primary_h = final_state.get("selected_hypothesis", {}) or {}
    hypotheses = final_state.get("hypotheses", []) or []
    conf_source = final_state.get("confidence_source", "llm")
    analysis_status = final_state.get("analysis_status", "success")
    failed_nodes = final_state.get("failed_llm_nodes", [])
    trace = final_state.get("execution_trace", []) or []
    
    is_degraded = analysis_status == "degraded" or conf_source == "fallback" or len(failed_nodes) > 0
    status_str = "degraded" if is_degraded else "completed"
    
    # 4. Construct Primary Root Cause
    title_str = primary_h.get("title", f"Outage on {input_data.affected_service}")
    likely_rc = primary_h.get("likely_root_cause") or ""
    
    root_cause_title = title_str if likely_rc.lower() in title_str.lower() or not likely_rc else f"{title_str} — {likely_rc}"
    root_cause_exp = primary_h.get("description") or likely_rc or input_data.description
    if likely_rc and likely_rc not in root_cause_exp:
        root_cause_exp = f"{likely_rc}. {root_cause_exp}"
        
    confidence_val = float(final_state.get("confidence", primary_h.get("confidence", 0.0)))
    
    sup_ids = primary_h.get("supporting_evidence_ids", [])
    if not sup_ids:
        sup_ids = [e.get("evidence_id") for e in accepted_evidence if e.get("evidence_id")]
        
    con_ids = primary_h.get("contradicting_evidence_ids", [])
    verif = [primary_h.get("recommended_next_check")] if primary_h.get("recommended_next_check") else ["Verify active metrics."]
    if final_report.get("recommended_verification"):
        verif.append(final_report.get("recommended_verification"))
        
    primary_rc = PrimaryRootCause(
        title=root_cause_title,
        explanation=root_cause_exp,
        confidence=confidence_val,
        confidence_explanation=f"Calculated from {len(sup_ids)} supporting evidence items and {len(con_ids)} contradictions." if not is_degraded else "Degraded fallback mode active due to LLM rate limit or unavailability.",
        supporting_evidence_ids=sup_ids,
        contradicting_evidence_ids=con_ids,
        affected_services=[input_data.affected_service],
        verification=verif,
    )
    
    # 5. Construct Alternative Hypotheses
    alt_hypotheses: List[AlternativeHypothesis] = []
    for h in hypotheses:
        if h.get("hypothesis_id") != primary_h.get("hypothesis_id"):
            alt_hypotheses.append(AlternativeHypothesis(
                title=h.get("title", "Alternative Cause"),
                explanation=h.get("description", h.get("likely_root_cause", "Evaluated hypothesis")),
                confidence=float(h.get("confidence", 0.0)),
                supporting_evidence_ids=h.get("supporting_evidence_ids", []),
                contradicting_evidence_ids=h.get("contradicting_evidence_ids", []),
            ))
            
    # 6. Construct Evidence Chain & Recommendations
    evidence_chain = [f"[{e.get('evidence_id')}] {e.get('source_name')}: {str(e.get('content'))[:100]}" for e in accepted_evidence]
    
    rec_actions: List[RecommendedAction] = []
    if primary_h.get("recommended_next_check"):
        rec_actions.append(RecommendedAction(
            category="Immediate",
            action=primary_h.get("recommended_next_check"),
            reason="Primary hypothesis verification check"
        ))
    if final_report.get("recommended_remediation"):
        rec_actions.append(RecommendedAction(
            category="Long-term",
            action=final_report.get("recommended_remediation"),
            reason="Permanent issue resolution and prevention"
        ))
        
    uncertainties = final_report.get("investigation_limitations", [])
    if is_degraded:
        uncertainties.append(f"LLM analysis failed on nodes: {failed_nodes}. Result is operating under degraded mode.")
        
    metadata = AnalysisMetadata(
        confidence_source=conf_source,
        nodes_executed=len(trace),
        execution_time_seconds=round(exec_duration, 2),
        failed_llm_nodes=failed_nodes,
    )
    
    exec_summary = final_report.get("incident_summary") or final_state.get("investigation_summary") or f"Root Cause Analysis complete for {input_data.title}."
    
    return EngineInvestigationOutput(
        incident_id=input_data.incident_id,
        status=status_str,
        analysis_complete=not is_degraded,
        failure_reason=f"LLM error on nodes: {failed_nodes}" if is_degraded else None,
        executive_summary=exec_summary,
        primary_root_cause=primary_rc,
        alternative_hypotheses=alt_hypotheses,
        timeline=[f"Event detected at {input_data.timeline}"],
        evidence_chain=evidence_chain,
        recommended_actions=rec_actions,
        uncertainties=uncertainties,
        analysis_metadata=metadata,
    )
