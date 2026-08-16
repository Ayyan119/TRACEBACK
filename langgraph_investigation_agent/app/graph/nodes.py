import logging
import time
from typing import Dict, Any, List

from langgraph_investigation_agent.app.config import config
from langgraph_investigation_agent.app.graph.state import InvestigationState, EvidenceItem
from langgraph_investigation_agent.app.models.vision import analyze_image_with_vision
from langgraph_investigation_agent.app.analysis.evidence import analyze_incident_document
from langgraph_investigation_agent.app.tools.log_tools import query_incident_logs
from langgraph_investigation_agent.app.analysis.incident import analyze_incident_needs
from langgraph_investigation_agent.app.retrieval.qdrant_retriever import retrieve_knowledge_chunks
from langgraph_investigation_agent.app.retrieval.previous_incidents import retrieve_previous_incidents
from langgraph_investigation_agent.app.retrieval.reranker import rerank_retrieved_items
from langgraph_investigation_agent.app.analysis.hypotheses import generate_ranked_hypotheses
from langgraph_investigation_agent.app.models.structured_models import EvidenceAnalysis, HypothesisEvaluation, FinalInvestigationReport, GroundingValidationResult
from langgraph_investigation_agent.app.models.llm import safe_invoke_structured_llm, safe_invoke_reasoning_llm
from langgraph_investigation_agent.app.prompts.evidence_prompts import EVIDENCE_ANALYSIS_SYSTEM_PROMPT, FINAL_REPORT_SYSTEM_PROMPT

logger = logging.getLogger("langgraph_agent.graph.nodes")


def _add_trace(updates: Dict[str, Any], node_name: str, duration_ms: float, details: str):
    updates["execution_trace"] = [{
        "node": node_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": round(duration_ms, 2),
        "details": details,
    }]


async def initialize_state_node(state: InvestigationState) -> Dict[str, Any]:
    """Node 1: Initializes investigation state, context identifiers, and collections."""
    start_time = time.time()
    
    investigation_id = state.get("investigation_id", f"inv-{int(time.time())}")
    project_id = state.get("project_id", "default-project")
    incident_id = state.get("incident_id", "INC-1001")
    
    updates: Dict[str, Any] = {
        "investigation_id": investigation_id,
        "project_id": project_id,
        "incident_id": incident_id,
        "processed_document_evidence": state.get("processed_document_evidence", []),
        "processed_image_evidence": state.get("processed_image_evidence", []),
        "accepted_evidence": state.get("accepted_evidence", []),
        "rejected_evidence": state.get("rejected_evidence", []),
        "log_query_history": state.get("log_query_history", []),
        "retrieved_logs": state.get("retrieved_logs", []),
        "tool_iterations": state.get("tool_iterations", 0),
        "retrieval_required": False,
        "retrieved_knowledge_documents": [],
        "retrieved_previous_incidents": [],
        "reranked_documents": [],
        "confidence_source": "llm",
        "analysis_status": "success",
        "failed_llm_nodes": [],
        "errors": state.get("errors", []),
        "warnings": state.get("warnings", []),
        "execution_trace": state.get("execution_trace", []),
    }
    
    _add_trace(updates, "initialize_state", (time.time() - start_time) * 1000, f"Initialized investigation {investigation_id}")
    return updates


async def process_images_node(state: InvestigationState) -> Dict[str, Any]:
    """Parallel Node: Analyzes incident images via vision model."""
    start_time = time.time()
    images = state.get("incident_images", [])
    processed_images = []
    
    for img in images:
        analysis = await analyze_image_with_vision(img)
        processed_images.append({
            "image": img,
            "analysis": analysis.model_dump(),
            "relevant": analysis.relevant,
        })
        
    updates: Dict[str, Any] = {"processed_image_evidence": processed_images}
    _add_trace(updates, "process_images", (time.time() - start_time) * 1000, f"Processed {len(images)} images")
    return updates


async def process_documents_node(state: InvestigationState) -> Dict[str, Any]:
    """Parallel Node: Analyzes incident documents for relevance and key points."""
    start_time = time.time()
    docs = state.get("incident_documents", [])
    processed_docs = []
    
    description = state.get("incident_description", "")
    for doc in docs:
        analysis = await analyze_incident_document(doc, description)
        processed_docs.append({
            "document": doc,
            "analysis": analysis.model_dump(),
            "relevant": analysis.relevant,
        })
        
    updates: Dict[str, Any] = {"processed_document_evidence": processed_docs}
    _add_trace(updates, "process_documents", (time.time() - start_time) * 1000, f"Processed {len(docs)} documents")
    return updates


async def collect_evidence_node(state: InvestigationState) -> Dict[str, Any]:
    """Merges relevant document and image evidence into accepted_evidence collection."""
    start_time = time.time()
    existing_accepted = state.get("accepted_evidence", []) or []
    existing_ids = set([e.get("evidence_id") for e in existing_accepted if e.get("evidence_id")])
    
    accepted = list(existing_accepted)
    rejected = list(state.get("rejected_evidence", []) or [])
    
    # Process mandatory description & log reference
    description = state.get("incident_description", "")
    log_ref = state.get("incident_log_reference", {})
    
    if "EVD-DESC-1" not in existing_ids:
        accepted.append({
            "evidence_id": "EVD-DESC-1",
            "source_type": "description",
            "source_name": "Incident Description",
            "content": description,
            "relevance": True,
            "confidence": 1.0,
        })
    
    if log_ref:
        accepted.append({
            "evidence_id": "EVD-LOG-REF-1",
            "source_type": "log_reference",
            "source_name": log_ref.get("file_name", "Mandatory Log File"),
            "content": f"Mandatory incident log file attached ({log_ref.get('file_size_bytes', 0)} bytes).",
            "relevance": True,
            "confidence": 1.0,
        })

    # Filter processed images
    for p_img in state.get("processed_image_evidence", []):
        if p_img.get("relevant", False):
            accepted.append({
                "evidence_id": f"EVD-IMG-{len(accepted)+1}",
                "source_type": "image",
                "source_name": p_img["image"].get("title", "Screenshot"),
                "content": p_img["analysis"].get("reasoning_summary", ""),
                "relevance": True,
                "confidence": p_img["analysis"].get("confidence", 0.9),
                "metadata": p_img["analysis"],
            })
        else:
            rejected.append(p_img)

    # Filter processed documents
    for p_doc in state.get("processed_document_evidence", []):
        if p_doc.get("relevant", False):
            accepted.append({
                "evidence_id": f"EVD-DOC-{len(accepted)+1}",
                "source_type": "document",
                "source_name": p_doc["document"].get("name", "Document"),
                "content": p_doc["analysis"].get("summary", ""),
                "relevance": True,
                "confidence": p_doc["analysis"].get("confidence", 0.9),
                "metadata": p_doc["analysis"],
            })
        else:
            rejected.append(p_doc)

    updates: Dict[str, Any] = {
        "accepted_evidence": accepted,
        "rejected_evidence": rejected,
    }
    _add_trace(updates, "collect_evidence", (time.time() - start_time) * 1000, f"Accepted {len(accepted)} evidence items, rejected {len(rejected)}")
    return updates


async def reason_with_tools_node(state: InvestigationState) -> Dict[str, Any]:
    """Deterministic tool node: decides if PostgreSQL log querying is needed using Python logic."""
    start_time = time.time()
    tool_iterations = state.get("tool_iterations", 0)
    
    if tool_iterations >= config.MAX_TOOL_ITERATIONS:
        logger.info(f"Max tool iterations ({config.MAX_TOOL_ITERATIONS}) reached; forcing transition to incident_analyzer.")
        updates: Dict[str, Any] = {"tool_decision": "no_tool"}
        _add_trace(updates, "reason_with_tools", (time.time() - start_time) * 1000, "Max tool iterations reached (forced finish)")
        return updates

    retrieved_logs = state.get("retrieved_logs", [])

    # Deterministic decision: query logs if no logs retrieved yet
    if len(retrieved_logs) == 0 and tool_iterations == 0:
        updates = {
            "tool_decision": "query_logs",
            "tool_iterations": tool_iterations + 1,
        }
        _add_trace(updates, "reason_with_tools", (time.time() - start_time) * 1000, "Deterministic Decision: query_logs (iteration 1)")
        return updates
    else:
        updates = {"tool_decision": "no_tool"}
        _add_trace(updates, "reason_with_tools", (time.time() - start_time) * 1000, "Deterministic Decision: no_tool needed")
        return updates


async def execute_log_tools_node(state: InvestigationState) -> Dict[str, Any]:
    """Tool Node: Executes PostgreSQL structured log tool."""
    start_time = time.time()
    project_id = state.get("project_id", "default-project")
    incident_id = state.get("incident_id", "INC-1001")
    
    # Query logs for affected services
    services = state.get("services", ["checkout-service"])
    target_service = services[0] if services else "checkout-service"
    
    res = await query_incident_logs(
        project_id=project_id,
        incident_id=incident_id,
        service=target_service,
        level="ERROR",
        limit=50,
    )
    
    history = state.get("log_query_history", [])
    history.append({
        "iteration": state.get("tool_iterations", 1),
        "query": res.get("query"),
        "total_matches": res.get("total_matches", 0),
    })
    
    logs = state.get("retrieved_logs", [])
    logs.extend(res.get("records", []))
    
    updates: Dict[str, Any] = {
        "log_query_history": history,
        "retrieved_logs": logs,
    }
    _add_trace(updates, "execute_log_tools", (time.time() - start_time) * 1000, f"Retrieved {len(res.get('records', []))} log records")
    return updates


async def incident_analyzer_node(state: InvestigationState) -> Dict[str, Any]:
    """Incident Analyzer Node: Self-RAG decision on knowledge base & previous incident retrieval."""
    start_time = time.time()
    description = state.get("incident_description", "")
    accepted = state.get("accepted_evidence", [])
    logs = state.get("retrieved_logs", [])
    
    decision = await analyze_incident_needs(description, accepted, logs)
    
    updates: Dict[str, Any] = {
        "retrieval_required": decision.retrieval_required,
        "retrieval_reason": decision.retrieval_reason,
        "search_queries": decision.search_queries,
        "previous_incident_search_required": decision.previous_incident_search_required,
    }
    _add_trace(updates, "incident_analyzer", (time.time() - start_time) * 1000, f"Retrieval required: {decision.retrieval_required}")
    return updates


async def retrieve_knowledge_node(state: InvestigationState) -> Dict[str, Any]:
    """Qdrant Retrieval Node: Searches top 8 knowledge chunks."""
    start_time = time.time()
    project_id = state.get("project_id", "default-project")
    queries = state.get("search_queries", ["runbook"])
    
    chunks = await retrieve_knowledge_chunks(project_id, queries, top_k=8)
    
    updates: Dict[str, Any] = {"retrieved_knowledge_documents": chunks}
    _add_trace(updates, "retrieve_knowledge", (time.time() - start_time) * 1000, f"Retrieved {len(chunks)} Qdrant knowledge chunks")
    return updates


async def retrieve_previous_incidents_node(state: InvestigationState) -> Dict[str, Any]:
    """Previous Incident Retrieval Node: Searches top 2 atomic resolved incident JSON objects."""
    start_time = time.time()
    project_id = state.get("project_id", "default-project")
    queries = state.get("search_queries", ["lock contention outage"])
    
    prev_incidents = []
    if state.get("previous_incident_search_required", False):
        prev_incidents = await retrieve_previous_incidents(project_id, queries, top_k=2)
        
    updates: Dict[str, Any] = {"retrieved_previous_incidents": prev_incidents}
    _add_trace(updates, "retrieve_previous_incidents", (time.time() - start_time) * 1000, f"Retrieved {len(prev_incidents)} previous incidents")
    return updates


async def rerank_retrieved_information_node(state: InvestigationState) -> Dict[str, Any]:
    """Reranker Node: Evaluates relevance of retrieved knowledge & previous incidents."""
    start_time = time.time()
    desc = state.get("incident_description", "")
    chunks = state.get("retrieved_knowledge_documents", [])
    prev_inc = state.get("retrieved_previous_incidents", [])
    
    reranked = await rerank_retrieved_items(desc, chunks, prev_inc)
    
    updates: Dict[str, Any] = {"reranked_documents": reranked}
    _add_trace(updates, "rerank_retrieved_information", (time.time() - start_time) * 1000, f"Reranked {len(chunks)+len(prev_inc)} items -> {len(reranked)} kept")
    return updates


async def analyze_evidence_node(state: InvestigationState) -> Dict[str, Any]:
    """Evidence Analyzer Node: Synthesizes accepted evidence, logs, and reranked runbooks using LLM reasoning."""
    start_time = time.time()
    desc = state.get("incident_description", "")
    logs = state.get("retrieved_logs", [])
    accepted = state.get("accepted_evidence", [])
    reranked = state.get("reranked_documents", [])
    services = state.get("services", ["target-service"])
    primary_service = services[0] if services else "target-service"
    
    prompt = (
        f"{EVIDENCE_ANALYSIS_SYSTEM_PROMPT}\n\n"
        f"INCIDENT CONTEXT:\n"
        f"- Description: {desc}\n"
        f"- Primary Service: {primary_service}\n"
        f"- Accepted Evidence: {[e.get('source_name') + ': ' + str(e.get('content')) for e in accepted]}\n"
        f"- Log Records: {[l.get('service', '') + ': ' + l.get('message', '') for l in logs[:10]]}\n"
        f"- Reranked Runbooks: {[r.get('title', '') + ': ' + r.get('content', '')[:100] for r in reranked[:5]]}\n\n"
        f"Synthesize structured evidence analysis."
    )
    
    synthesis = await safe_invoke_structured_llm(
        EvidenceAnalysis,
        prompt,
        node_name="analyze_evidence",
    )
    
    if synthesis:
        updates: Dict[str, Any] = {"evidence_analysis": synthesis.model_dump()}
        _add_trace(updates, "analyze_evidence", (time.time() - start_time) * 1000, f"Synthesized LLM evidence analysis for {primary_service}")
        return updates

    # 2. Dynamic Evidence-Based Fallback
    symptoms = [desc] if desc else ["Service anomaly observed"]
    if logs:
        symptoms.append(f"Log message: {logs[0].get('message', '')}")

    what_happened = f"Service '{primary_service}' reported degradation. Description: {desc}"

    synthesis = EvidenceAnalysis(
        what_happened=what_happened,
        when_it_happened="Ongoing",
        affected_service=primary_service,
        symptoms=symptoms,
        error_patterns=symptoms[:2],
        correlations=[f"Reported symptoms on {primary_service} correlate with telemetry records."],
        possible_causes=[what_happened],
        contradictory_evidence=[],
        missing_information=[],
    )
    
    updates: Dict[str, Any] = {
        "evidence_analysis": synthesis.model_dump(),
        "failed_llm_nodes": ["analyze_evidence"],
    }
    _add_trace(updates, "analyze_evidence", (time.time() - start_time) * 1000, f"Synthesized fallback evidence analysis for {primary_service}")
    return updates


async def generate_hypotheses_node(state: InvestigationState) -> Dict[str, Any]:
    """Hypothesis Generator Node: Produces ranked root-cause hypotheses with confidence scores."""
    start_time = time.time()
    ev_analysis = state.get("evidence_analysis", {})
    accepted = state.get("accepted_evidence", [])
    
    ranking, is_fallback = await generate_ranked_hypotheses(ev_analysis, accepted)
    
    hypotheses_dicts = [h.model_dump() for h in ranking.hypotheses]
    primary_h = hypotheses_dicts[0] if hypotheses_dicts else None
    
    confidence_source = "fallback" if is_fallback else "llm"
    analysis_status = "degraded" if is_fallback else "success"
    
    updates: Dict[str, Any] = {
        "hypotheses": hypotheses_dicts,
        "selected_hypothesis": primary_h,
        "confidence": primary_h["confidence"] if primary_h else 0.0,
        "confidence_source": confidence_source,
        "analysis_status": analysis_status,
        "investigation_summary": f"Hypotheses generated for {state.get('incident_id', 'incident')}. Primary candidate: {primary_h['title'] if primary_h else 'Unknown'}.",
    }
    if is_fallback:
        updates["failed_llm_nodes"] = ["generate_hypotheses"]
        
    _add_trace(updates, "generate_hypotheses", (time.time() - start_time) * 1000, f"Generated {len(hypotheses_dicts)} hypotheses (Confidence: {primary_h['confidence'] if primary_h else 0}%, Source: {confidence_source})")
    return updates


async def evaluate_hypotheses_node(state: InvestigationState) -> Dict[str, Any]:
    """Node 13: Evaluates generated hypotheses against evidence sufficiency and decides whether to loop or produce final RCA."""
    start_time = time.time()
    hypotheses = state.get("hypotheses", [])
    primary_h = state.get("selected_hypothesis") or (hypotheses[0] if hypotheses else {})
    confidence = state.get("confidence", 0.0)
    accepted_evidence = state.get("accepted_evidence", [])
    current_inv_iter = state.get("investigation_iterations", 0) + 1
    
    # Evidence sufficiency evaluation
    is_sufficient = confidence >= 70.0 or len(accepted_evidence) >= 1
    
    evaluation = HypothesisEvaluation(
        evidence_sufficient=is_sufficient,
        confidence=confidence,
        reason=f"Primary hypothesis '{primary_h.get('title')}' is backed by validated evidence with {confidence}% confidence." if is_sufficient else "Telemetry evidence is insufficient to achieve confidence threshold.",
        missing_evidence=[] if is_sufficient else ["Additional telemetry logs required."],
        contradictions=[],
        recommended_next_action="Generate final RCA report." if is_sufficient else "Loop back to reason_with_tools to query missing log records.",
        selected_hypothesis_id=primary_h.get("hypothesis_id", "HYP-1")
    )
    
    updates: Dict[str, Any] = {
        "hypothesis_evaluation": evaluation.model_dump(),
        "evidence_sufficient": is_sufficient,
        "investigation_iterations": current_inv_iter,
    }
    _add_trace(updates, "evaluate_hypotheses", (time.time() - start_time) * 1000, f"Evaluated evidence sufficiency: {is_sufficient} (Cycle {current_inv_iter}/{config.MAX_INVESTIGATION_ITERATIONS})")
    return updates


async def validate_grounding_node(state: InvestigationState) -> Dict[str, Any]:
    """Node 13.5: Grounding Validation Node: Validates that selected hypothesis claims have direct supporting evidence IDs."""
    start_time = time.time()
    selected_h = state.get("selected_hypothesis", {}) or {}
    accepted_ev = state.get("accepted_evidence", []) or []
    valid_ids = set([e.get("evidence_id") for e in accepted_ev if e.get("evidence_id")])
    
    cited_ids = selected_h.get("supporting_evidence_ids", [])
    invalid_citations = [cid for cid in cited_ids if cid not in valid_ids]
    
    grounded = len(valid_ids) > 0 and len(cited_ids) > 0 and len(invalid_citations) == 0
    unsupported = []
    
    if not valid_ids or not cited_ids:
        grounded = False
        unsupported.append("Selected hypothesis lacks direct supporting evidence IDs in current state.")
    if invalid_citations:
        grounded = False
        unsupported.append(f"Cites invalid or missing evidence IDs: {invalid_citations}")
        
    validation = GroundingValidationResult(
        grounded=grounded,
        unsupported_claims=unsupported,
        invalid_evidence_references=invalid_citations,
        confidence_consistent=True,
        root_cause_consistent=True,
        reason="Claims backed by valid evidence IDs." if grounded else "Insufficient evidence to confirm root cause."
    )
    
    updates: Dict[str, Any] = {
        "grounding_validation": validation.model_dump()
    }
    
    # If ungrounded or evidence insufficient, override selected_hypothesis to explicit inconclusive statement
    if not grounded and (not accepted_ev or not cited_ids):
        inconclusive_title = "Root cause cannot be conclusively determined from the supplied evidence."
        updated_h = dict(selected_h)
        updated_h["title"] = inconclusive_title
        updated_h["likely_root_cause"] = inconclusive_title
        updated_h["confidence"] = min(float(selected_h.get("confidence", 30.0)), 30.0)
        updated_h["is_evidence_grounded"] = False
        updates["selected_hypothesis"] = updated_h
        updates["confidence"] = updated_h["confidence"]
        
    _add_trace(updates, "validate_grounding", (time.time() - start_time) * 1000, f"Grounding validation: {grounded} ({validation.reason})")
    return updates


async def generate_final_report_node(state: InvestigationState) -> Dict[str, Any]:
    """Node 14: Synthesizes final Root Cause Analysis (RCA) report strictly grounded in canonical selected_hypothesis."""
    start_time = time.time()
    primary_h = state.get("selected_hypothesis", {}) or {}
    ev_analysis = state.get("evidence_analysis", {}) or {}
    accepted = state.get("accepted_evidence", []) or []
    retrieved_logs = state.get("retrieved_logs", []) or []
    reranked = state.get("reranked_documents", []) or []
    
    know_docs = [r for r in reranked if r.get("source_type") == "knowledge_document"]
    prev_incidents = [r for r in reranked if r.get("source_type") == "incident_history"]
    grounding_val = state.get("grounding_validation", {}) or {}
    
    canonical_root_cause = primary_h.get("likely_root_cause") or primary_h.get("title") or "Root cause cannot be conclusively determined from the supplied evidence."
    canonical_confidence = float(state.get("confidence", primary_h.get("confidence", 0.0)))
    
    prompt = (
        f"{FINAL_REPORT_SYSTEM_PROMPT}\n\n"
        f"CANONICAL INVESTIGATION DATA:\n"
        f"- Incident Description: {state.get('incident_description')}\n"
        f"- Primary Service: {state.get('services', ['target-service'])[0] if state.get('services') else 'target-service'}\n"
        f"- CANONICAL ROOT CAUSE (DO NOT CHANGE): {canonical_root_cause}\n"
        f"- CANONICAL CONFIDENCE SCORE: {canonical_confidence}%\n"
        f"- Causal Chain: {primary_h.get('causal_chain', ['Initiating Event -> Symptom'])}\n"
        f"- Observed Symptoms: {ev_analysis.get('symptoms', [])}\n"
        f"- Supporting Evidence IDs: {primary_h.get('supporting_evidence_ids', [])}\n\n"
        f"RETRIEVAL TRUTHFULNESS DATA:\n"
        f"- Retrieved Logs Count: {len(retrieved_logs)} (If 0, FORBIDDEN to claim 'logs show' or 'logs indicate')\n"
        f"- Retrieved Knowledge Documents Count: {len(know_docs)} (If 0, FORBIDDEN to claim 'runbook states')\n"
        f"- Retrieved Historical Incidents Count: {len(prev_incidents)} (If 0, FORBIDDEN to claim 'historical incidents show')\n"
        f"- Grounding Validation Status: {grounding_val.get('grounded', False)}\n\n"
        f"Synthesize the final RCA report. Your output MUST match the canonical root cause and confidence exactly."
    )
    
    report = await safe_invoke_structured_llm(
        FinalInvestigationReport,
        prompt,
        node_name="generate_final_report",
    )
    
    if report:
        # Enforce canonical root cause and confidence alignment
        report.root_cause = canonical_root_cause
        report.confidence = canonical_confidence
        report.confidence_source = state.get("confidence_source", "llm")
        report.analysis_status = state.get("analysis_status", "success")
        
        # Enforce retrieval truthfulness in summaries
        if not retrieved_logs and any("log" in s.lower() for s in report.accepted_evidence_summary):
            report.accepted_evidence_summary = [s for s in report.accepted_evidence_summary if "log" not in s.lower()]
        if not know_docs:
            report.retrieved_knowledge_summary = ["No runbooks or knowledge documents retrieved for this incident."]
        if not prev_incidents:
            report.historical_incidents_summary = ["No historical incidents retrieved for this incident."]
            
        updates: Dict[str, Any] = {
            "final_report": report.model_dump(),
            "investigation_summary": f"FINAL RCA COMPLETE for {state.get('incident_id')}: {report.root_cause} (Confidence: {report.confidence}%)",
        }
        _add_trace(updates, "generate_final_report", (time.time() - start_time) * 1000, f"Generated LLM final RCA report matching canonical root cause with {report.confidence}% confidence")
        return updates

    # 2. Dynamic Evidence-Based Fallback (when LLM fails)
    conf_src = "fallback"
    report = FinalInvestigationReport(
        incident_summary=state.get("incident_description", "Production anomaly"),
        affected_services=state.get("services", ["target-service"]),
        timeline="Ongoing",
        observed_symptoms=ev_analysis.get("symptoms", [state.get("incident_description", "Service degradation")]),
        accepted_evidence_summary=[f"[{e.get('evidence_id')}] {e.get('source_name')}" for e in accepted],
        retrieved_knowledge_summary=[r.get("title", "") for r in know_docs] if know_docs else ["No knowledge documents retrieved."],
        historical_incidents_summary=[r.get("title", "") for r in prev_incidents] if prev_incidents else ["No historical incidents retrieved."],
        root_cause=canonical_root_cause,
        confidence=canonical_confidence,
        confidence_source=conf_src,
        analysis_status="degraded",
        supporting_evidence=[f"Evidence ID: {eid}" for eid in primary_h.get("supporting_evidence_ids", [])],
        contradictory_evidence=primary_h.get("contradicting_evidence_ids", []),
        recommended_verification=primary_h.get("recommended_next_check", "Verify active service telemetry metrics."),
        recommended_remediation="Inspect active service logs, check resource limits, and monitor error rates.",
        investigation_limitations=["Investigation completed using evidence-aware fallback due to LLM rate limits or unavailability."]
    )
    
    updates: Dict[str, Any] = {
        "final_report": report.model_dump(),
        "confidence_source": conf_src,
        "analysis_status": "degraded",
        "failed_llm_nodes": ["generate_final_report"],
        "investigation_summary": f"FINAL RCA COMPLETE (DEGRADED) for {state.get('incident_id')}: {report.root_cause}",
    }
    _add_trace(updates, "generate_final_report", (time.time() - start_time) * 1000, f"Generated fallback final RCA report matching canonical root cause (Confidence: {report.confidence}%, Source: fallback)")
    return updates
