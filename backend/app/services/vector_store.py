import logging
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Real Qdrant Vector Store service for TRACEBACK RAG ingestion & similarity search."""

    COLLECTION_NAME = "traceback_vectors"

    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self._initialized = False

    def get_client(self) -> QdrantClient:
        if self._client is None:
            url = getattr(settings, "QDRANT_URL", "http://localhost:6333")
            api_key = getattr(settings, "QDRANT_API_KEY", "") or None
            logger.info(f"Connecting to Qdrant at '{url}'...")
            self._client = QdrantClient(url=url, api_key=api_key)
        return self._client

    def ensure_collection(self, dimension: int) -> bool:
        """Verifies or creates the unified Qdrant vector collection matching embedding dimension."""
        client = self.get_client()
        try:
            collections = client.get_collections().collections
            exists = any(c.name == self.COLLECTION_NAME for c in collections)

            if not exists:
                logger.info(f"Creating Qdrant collection '{self.COLLECTION_NAME}' (dim={dimension}, metric=COSINE)...")
                client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=qmodels.VectorParams(
                        size=dimension,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
            else:
                # Verify dimension match
                info = client.get_collection(collection_name=self.COLLECTION_NAME)
                existing_size = info.config.params.vectors.size
                if existing_size != dimension:
                    logger.warning(f"Qdrant collection size mismatch! Existing: {existing_size}, Model: {dimension}. Recreating...")
                    client.delete_collection(collection_name=self.COLLECTION_NAME)
                    client.create_collection(
                        collection_name=self.COLLECTION_NAME,
                        vectors_config=qmodels.VectorParams(
                            size=dimension,
                            distance=qmodels.Distance.COSINE,
                        ),
                    )

            # Ensure payload field indexes exist for project isolation and source lookup
            for field_name in ["project_id", "source_type", "source_id", "knowledge_document_id"]:
                try:
                    client.create_payload_index(
                        collection_name=self.COLLECTION_NAME,
                        field_name=field_name,
                        field_schema=qmodels.PayloadSchemaType.KEYWORD,
                    )
                except Exception:
                    pass

            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")
            raise e

    def delete_source_vectors(self, source_type: str, source_id: str) -> bool:
        """Deletes all chunks belonging to a specific source document or evidence ID before re-indexing."""
        client = self.get_client()
        try:
            filter_cond = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(key="source_type", match=qmodels.MatchValue(value=source_type)),
                    qmodels.FieldCondition(key="source_id", match=qmodels.MatchValue(value=source_id)),
                ]
            )
            client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=qmodels.FilterSelector(filter=filter_cond),
            )
            logger.info(f"Deleted old vectors for {source_type}:{source_id}")
            return True
        except Exception as e:
            logger.warning(f"Vector deletion warning for {source_type}:{source_id}: {e}")
            return False

    def upsert_chunks(
        self,
        points: List[qmodels.PointStruct],
    ) -> bool:
        """Upserts a batch of vector points with payload metadata into Qdrant."""
        if not points:
            return True
        client = self.get_client()
        try:
            client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points,
            )
            logger.info(f"Successfully upserted {len(points)} vector points into Qdrant.")
            return True
        except Exception as e:
            logger.error(f"Qdrant upsert failed: {e}")
            raise e

    def search_similar(
        self,
        query_vector: List[float],
        project_id: str,
        top_k: int = 5,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Executes a similarity search against Qdrant scoped to project_id."""
        client = self.get_client()
        try:
            must_conditions = [
                qmodels.FieldCondition(key="project_id", match=qmodels.MatchValue(value=project_id))
            ]
            if source_type:
                must_conditions.append(
                    qmodels.FieldCondition(key="source_type", match=qmodels.MatchValue(value=source_type))
                )

            search_filter = qmodels.Filter(must=must_conditions)

            # Support both qdrant-client query_points / search methods
            if hasattr(client, "search"):
                res = client.search(
                    collection_name=self.COLLECTION_NAME,
                    query_vector=query_vector,
                    query_filter=search_filter,
                    limit=top_k,
                )
            else:
                res = client.query_points(
                    collection_name=self.COLLECTION_NAME,
                    query=query_vector,
                    query_filter=search_filter,
                    limit=top_k,
                ).points

            output = []
            for hit in res:
                payload = hit.payload or {}
                output.append({
                    "id": str(hit.id),
                    "score": round(float(hit.score), 4),
                    "text": payload.get("text", ""),
                    "metadata": payload,
                })
            return output
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []


vector_store = VectorStore()
