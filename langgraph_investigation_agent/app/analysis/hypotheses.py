import logging
from typing import List, Dict, Any, Tuple
from langgraph_investigation_agent.app.models.structured_models import Hypothesis, HypothesisRanking
from langgraph_investigation_agent.app.models.llm import safe_invoke_structured_llm
from langgraph_investigation_agent.app.prompts.hypothesis_prompts import HYPOTHESIS_GENERATION_SYSTEM_PROMPT

logger = logging.getLogger("langgraph_agent.analysis.hypotheses")


async def generate_ranked_hypotheses(
    evidence_analysis: Dict[str, Any],
    accepted_evidence: List[Dict[str, Any]],
) -> Tuple[HypothesisRanking, bool]:
    """
    Generates scenario-specific ranked root-cause hypotheses using structured LLM reasoning.
    Returns (HypothesisRanking, is_fallback_flag).
    """
    evidence_ids = [e.get("evidence_id", "EVD-1") for e in accepted_evidence]
    affected_service = evidence_analysis.get("affected_service", "target-service")
    what_happened = evidence_analysis.get("what_happened", "Production service outage")
    symptoms = evidence_analysis.get("symptoms", [])

    evidence_text_blocks = []
    for e in accepted_evidence:
        eid = e.get("evidence_id", "EVD-1")
        name = e.get("source_name", "Evidence")
        content = e.get("content", "")
        evidence_text_blocks.append(f"[{eid}] ({name}):\n{content}")
        
    evidence_formatted_str = "\n\n".join(evidence_text_blocks)

    valid_ids = [e.get("evidence_id") for e in accepted_evidence if e.get("evidence_id")]
    prompt = (
        f"{HYPOTHESIS_GENERATION_SYSTEM_PROMPT}\n\n"
        f"EVIDENCE ANALYSIS CONTEXT:\n"
        f"- Affected Service: {affected_service}\n"
        f"- What Happened: {what_happened}\n"
        f"- Observed Symptoms: {symptoms}\n"
        f"- ALL AVAILABLE EVIDENCE IDs: {valid_ids}\n\n"
        f"DETAILED EVIDENCE ITEMS:\n"
        f"{evidence_formatted_str}\n\n"
        f"Formulate 1 to 3 ranked hypotheses explaining the root cause. You MUST cite ALL matching evidence IDs from {valid_ids} in supporting_evidence_ids."
    )
    
    ranking = await safe_invoke_structured_llm(
        HypothesisRanking,
        prompt,
        node_name="generate_hypotheses",
    )
    
    if ranking and ranking.hypotheses:
        # Build normalized lookup for valid IDs
        valid_id_map = {str(eid).strip().lower(): eid for eid in valid_ids}
        
        for h in ranking.hypotheses:
            matched_ids = []
            for cited in h.supporting_evidence_ids:
                norm = str(cited).strip().lower()
                if norm in valid_id_map:
                    matched_ids.append(valid_id_map[norm])
                else:
                    # Check substring match (e.g., E-001 inside EVD-E-001 or vice versa)
                    for norm_val, real_val in valid_id_map.items():
                        if norm in norm_val or norm_val in norm:
                            matched_ids.append(real_val)
                            break
            
            # Deduplicate matched IDs preserving order
            h.supporting_evidence_ids = list(dict.fromkeys(matched_ids))
            
            # If accepted evidence was provided but LLM didn't cite exact IDs, associate accepted evidence IDs
            if not h.supporting_evidence_ids and accepted_evidence:
                h.supporting_evidence_ids = [e.get("evidence_id") for e in accepted_evidence if e.get("evidence_id")]
                
            h.is_evidence_grounded = len(h.supporting_evidence_ids) > 0

        primary = ranking.hypotheses[0]
        # Only flag inconclusive if accepted_evidence is truly empty or zero evidence was provided
        if not accepted_evidence:
            logger.warning("No accepted evidence available. Flagging root cause as inconclusive.")
            primary.title = "Root cause cannot be conclusively determined from the supplied evidence."
            primary.likely_root_cause = "Root cause cannot be conclusively determined from the supplied evidence."
            primary.confidence = 0.0
            primary.is_evidence_grounded = False

        logger.info(f"LLM generated {len(ranking.hypotheses)} hypotheses for '{affected_service}' (Primary: '{primary.title}', Conf: {primary.confidence}%, Grounded: {primary.is_evidence_grounded})")
        return ranking, False

    # 2. Dynamic Evidence-Based Fallback (No fake 75% confidence, confidence set to 0.0)
    logger.warning(f"LLM hypothesis generation unavailable for '{affected_service}'. Utilizing evidence-grounded fallback.")
    is_insufficient = not accepted_evidence or not evidence_ids
    title_text = "Root cause cannot be conclusively determined from the supplied evidence." if is_insufficient else f"Unverified Outage Cause on {affected_service}"
    h1 = Hypothesis(
        hypothesis_id="HYP-1",
        title=title_text,
        description=f"{what_happened}. Observed symptoms: {', '.join(symptoms[:2]) if symptoms else 'Service degradation'}.",
        confidence=0.0,
        supporting_evidence_ids=evidence_ids if not is_insufficient else [],
        contradicting_evidence_ids=[],
        affected_services=[affected_service],
        initiating_event="Unknown initiating event",
        causal_chain=["Telemetry evidence insufficient to establish causal chain"],
        likely_root_cause=what_happened if not is_insufficient else title_text,
        recommended_next_check=f"Collect additional system logs and metrics for {affected_service}.",
        is_evidence_grounded=not is_insufficient,
    )
    
    return HypothesisRanking(
        hypotheses=[h1],
        primary_hypothesis_id="HYP-1",
    ), True
