import logging
from typing import List, Dict, Any

logger = logging.getLogger("langgraph_agent.tools.knowledge_tools")

async def query_knowledge_base(project_id: str, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
    """Helper tool for knowledge base queries."""
    return [
        {
            "id": f"kb-{i}",
            "title": f"Runbook: {query} Resolution",
            "content": f"Standard operating procedure for {query}. Check database connection pool size, inspect P95 latency graphs, and restart degraded pods.",
            "category": "Runbook",
            "chunk_index": i,
            "score": 0.88 - (i * 0.02),
        }
        for i in range(1, min(top_k + 1, 9))
    ]
