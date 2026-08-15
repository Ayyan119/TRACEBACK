import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models

from app.config import config
from app.retrieval.qdrant_retriever import get_embedding_model

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
        
        return results
    except Exception as e:
        logger.warning(f"Qdrant previous incident retrieval unavailable for project '{project_id}': {e}")
        return []
