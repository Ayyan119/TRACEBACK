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
        logger.info(f"LLM generated {len(ranking.hypotheses)} hypotheses for '{affected_service}'")
        return ranking, False

    # 2. Dynamic Evidence-Based Fallback (No fake 75% confidence, confidence set to 0.0)
    logger.warning(f"LLM hypothesis generation unavailable for '{affected_service}'. Utilizing evidence-grounded fallback.")
    h1 = Hypothesis(
        hypothesis_id="HYP-1",
        title=f"Unverified Outage Cause on {affected_service}",
        description=f"{what_happened}. Observed symptoms: {', '.join(symptoms[:2]) if symptoms else 'Service degradation'}.",
        confidence=0.0,
        supporting_evidence_ids=evidence_ids,
        contradicting_evidence_ids=[],
        affected_services=[affected_service],
        likely_root_cause=what_happened or f"Unidentified runtime error on {affected_service}",
        recommended_next_check=f"Inspect system metrics and active logs for {affected_service}."
    )
    
    return HypothesisRanking(
        hypotheses=[h1],
        primary_hypothesis_id="HYP-1",
    ), True
