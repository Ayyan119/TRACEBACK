import logging
from typing import List, Dict, Any

logger = logging.getLogger("langgraph_agent.retrieval.reranker")


async def rerank_retrieved_items(
    description: str,
    knowledge_chunks: List[Dict[str, Any]],
    previous_incidents: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Reranks knowledge chunks and previous incidents to keep only highly relevant evidence items."""
    combined_candidates = []
    desc_words = set(description.lower().split())
    
    for item in knowledge_chunks:
        title = item.get("title", "")
        content = item.get("content", "")
        raw_score = item.get("score", 0.70)
        
        # Dynamic overlap / score calculation
        text = (title + " " + content).lower()
        match_count = sum(1 for w in desc_words if len(w) > 3 and w in text)
        adjusted_score = min(1.0, raw_score + (match_count * 0.05))
        
        keep = adjusted_score >= 0.60
        combined_candidates.append({
            "source_id": item.get("id", "chunk"),
            "source_type": "knowledge_document",
            "title": title,
            "content": content,
            "relevance_score": round(adjusted_score, 2),
            "relevance_reason": f"Semantic relevance score {adjusted_score:.2f} based on incident symptom terms." if keep else "Below relevance threshold (0.60).",
            "keep": keep,
        })
        
    for inc in previous_incidents:
        payload = inc.get("historical_payload", {})
        title = inc.get("title", payload.get("title", ""))
        root_cause = payload.get("root_cause_summary", "")
        raw_score = inc.get("score", 0.75)
        
        keep = raw_score >= 0.60
        combined_candidates.append({
            "source_id": inc.get("id", "prev-inc"),
            "source_type": "incident_history",
            "title": title,
            "content": f"Resolved Incident: {title}. Root Cause: {root_cause}",
            "relevance_score": round(raw_score, 2),
            "relevance_reason": f"Historical incident match score {raw_score:.2f}." if keep else "Below historical relevance threshold.",
            "keep": keep,
        })

    kept_items = [c for c in combined_candidates if c["keep"]]
    logger.info(f"Reranked {len(combined_candidates)} candidate items -> retained {len(kept_items)} items (threshold >= 0.60).")
    return kept_items
