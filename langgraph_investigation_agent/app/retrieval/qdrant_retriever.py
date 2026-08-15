import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models

from app.config import config

logger = logging.getLogger("langgraph_agent.retrieval.qdrant")

_embedding_model: Any = None


def get_embedding_model() -> Any:
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {e}")
            _embedding_model = None
    return _embedding_model


async def retrieve_knowledge_chunks(
    project_id: str,
    search_queries: List[str],
    top_k: int = 8,
) -> List[Dict[str, Any]]:
    """Retrieves top K knowledge document chunks from Qdrant vector database."""
    top_k = min(top_k, config.MAX_KNOWLEDGE_TOP_K)
    qdrant_url = config.QDRANT_URL or "http://localhost:6333"
    api_key = config.QDRANT_API_KEY if config.QDRANT_API_KEY else None
    
    try:
        client = QdrantClient(url=qdrant_url, api_key=api_key, timeout=10)
        model = get_embedding_model()
        
        combined_query = " ".join(search_queries) if search_queries else "incident runbook troubleshooting"
        vector = model.encode(combined_query).tolist() if model else [0.0] * 384
        
        filter_conditions = [
            rest_models.FieldCondition(
                key="project_id",
                match=rest_models.MatchValue(value=project_id),
            ),
            rest_models.FieldCondition(
                key="source_type",
                match=rest_models.MatchValue(value="knowledge_document"),
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
                "title": payload.get("title", "Knowledge Document"),
                "category": payload.get("category", "Runbook"),
                "content": payload.get("content", payload.get("text", "")),
                "source_type": "knowledge_document",
                "project_id": project_id,
            })
        
        return results
    except Exception as e:
        logger.warning(f"Qdrant knowledge retrieval unavailable for project '{project_id}': {e}")
        return []
