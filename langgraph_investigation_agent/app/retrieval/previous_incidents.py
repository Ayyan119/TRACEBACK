import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models

from langgraph_investigation_agent.app.config import config
from langgraph_investigation_agent.app.retrieval.qdrant_retriever import get_embedding_model

logger = logging.getLogger("langgraph_agent.retrieval.previous_incidents")


async def retrieve_previous_incidents(
    project_id: str,
    search_queries: List[str],
    top_k: int = 2,
) -> List[Dict[str, Any]]:
    """Retrieves complete resolved incident JSON objects (max 2) from Qdrant vector database."""
    top_k = min(top_k, config.MAX_PREVIOUS_INCIDENTS_TOP_K)
    qdrant_url = config.QDRANT_URL or "http://localhost:6333"
    api_key = config.QDRANT_API_KEY if config.QDRANT_API_KEY else None
    
    try:
        client = QdrantClient(url=qdrant_url, api_key=api_key, timeout=10)
        model = get_embedding_model()
        
        query = " ".join(search_queries) if search_queries else "database connection pool timeout latency"
        vector = model.encode(query).tolist() if model else [0.0] * 384
        
        filter_conditions = [
            rest_models.FieldCondition(
                key="project_id",
                match=rest_models.MatchValue(value=project_id),
            ),
            rest_models.FieldCondition(
                key="source_type",
                match=rest_models.MatchValue(value="incident_history"),
            ),
        ]

        try:
            search_results = client.query_points(
                collection_name=config.QDRANT_COLLECTION,
                query=vector,
                query_filter=rest_models.Filter(must=filter_conditions),
                limit=top_k,
            )
            hits = getattr(search_results, "points", search_results)
        except Exception:
            hits = client.search(
                collection_name=config.QDRANT_COLLECTION,
                query_vector=vector,
                query_filter=rest_models.Filter(must=filter_conditions),
                limit=top_k,
            )
        
        results = []
        for hit in hits:
            payload = hit.payload or {}
            results.append({
                "id": str(hit.id),
                "score": float(hit.score),
                "incident_code": payload.get("incident_code", "INC-HIST"),
                "title": payload.get("title", "Resolved Incident"),
                "status": payload.get("status", "Resolved"),
                "historical_payload": payload.get("historical_payload", payload),
                "source_type": "incident_history",
                "project_id": project_id,
            })
        
        diag = {
            "project_id": project_id,
            "query": query,
            "collection": config.QDRANT_COLLECTION,
            "filters": {"project_id": project_id, "source_type": "incident_history"},
            "top_k": top_k,
            "raw_results_count": len(hits),
            "filtered_results_count": len(results),
            "selected_results_count": len(results)
        }
        logger.info(f"QDRANT_INCIDENT_HISTORY_DIAGNOSTICS: {diag}")

        if len(results) == 0:
            logger.info(f"Qdrant previous incident retrieval returned 0 results for project '{project_id}' with query '{query}'. Reason: Collection '{config.QDRANT_COLLECTION}' may be unindexed or contains no matching 'incident_history' records for project_id='{project_id}'.")

        return results
    except Exception as e:
        diag = {
            "project_id": project_id,
            "query": search_queries,
            "collection": config.QDRANT_COLLECTION,
            "error": str(e),
            "selected_results_count": 0
        }
        logger.warning(f"Qdrant previous incident retrieval unavailable: {diag}")
        return []
