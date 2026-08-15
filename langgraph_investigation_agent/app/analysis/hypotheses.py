import logging
from typing import List, Dict, Any
from app.models.structured_models import Hypothesis, HypothesisRanking
from app.models.llm import get_structured_llm
from app.prompts.hypothesis_prompts import HYPOTHESIS_GENERATION_SYSTEM_PROMPT

logger = logging.getLogger("langgraph_agent.analysis.hypotheses")


async def generate_ranked_hypotheses(
    evidence_analysis: Dict[str, Any],
    accepted_evidence: List[Dict[str, Any]],
) -> HypothesisRanking:
    """Generates scenario-specific ranked root-cause hypotheses using structured LLM reasoning."""
    evidence_ids = [e.get("evidence_id", "EVD-1") for e in accepted_evidence]
    affected_service = evidence_analysis.get("affected_service", "target-service")
    what_happened = evidence_analysis.get("what_happened", "Production service outage")
    symptoms = evidence_analysis.get("symptoms", [])

    # 1. Attempt dynamic structured LLM call
    structured_llm = get_structured_llm(HypothesisRanking)
    if structured_llm is not None:
        try:
            prompt = (
                f"{HYPOTHESIS_GENERATION_SYSTEM_PROMPT}\n\n"
                f"EVIDENCE ANALYSIS CONTEXT:\n"
                f"- Affected Service: {affected_service}\n"
                f"- What Happened: {what_happened}\n"
                f"- Observed Symptoms: {symptoms}\n"
                f"- Available Evidence IDs: {evidence_ids}\n\n"
                f"Formulate 1 to 3 ranked hypotheses explaining the root cause based ONLY on the evidence above."
            )
            ranking = await structured_llm.ainvoke(prompt)
            if ranking and ranking.hypotheses:
                logger.info(f"LLM generated {len(ranking.hypotheses)} hypotheses for '{affected_service}'")
                return ranking
        except Exception as e:
            logger.warning(f"LLM hypothesis generation failed: {e}")

    # 2. Dynamic Evidence-Based Fallback (No hardcoded RCA strings)
    h1 = Hypothesis(
        hypothesis_id="HYP-1",
        title=f"Primary Outage Cause on {affected_service}",
        description=f"{what_happened}. Observed symptoms: {', '.join(symptoms[:2]) if symptoms else 'Service degradation'}.",
        confidence=75.0 if symptoms else 50.0,
        supporting_evidence_ids=evidence_ids,
        contradicting_evidence_ids=[],
        affected_services=[affected_service],
        likely_root_cause=what_happened or f"Unidentified runtime error on {affected_service}",
        recommended_next_check=f"Inspect system metrics and active logs for {affected_service}."
    )
    
    return HypothesisRanking(
        hypotheses=[h1],
        primary_hypothesis_id="HYP-1",
    )
