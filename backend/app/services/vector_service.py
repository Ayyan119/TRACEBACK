import logging
import math
import re
from typing import Any, Dict, List, Optional
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class VectorService:
    """Unified Vector Service providing embedding generation and Qdrant RAG similarity search for Stage 11 & Stage 12."""

    def search_similar(
        self,
        query: str,
        project_id: str,
        top_k: int = 5,
        source_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Executes a real vector similarity search against Qdrant using the BAAI/bge-small-en-v1.5 embedding model."""
        if not query or not query.strip():
            return []

        # Generate dense query embedding vector
        query_vector = embedding_service.embed_text(query)

        # Execute search in Qdrant
        return vector_store.search_similar(
            query_vector=query_vector,
            project_id=project_id,
            top_k=top_k,
            source_type=source_type,
        )

    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        """Splits text into overlapping chunks for RAG vector indexing."""
        from app.services.ingestion.chunker import chunker

        chunks = chunker.chunk_text(text, chunk_size=chunk_size, chunk_overlap=overlap)
        return [c.text for c in chunks]

    def compute_keyword_similarity(self, query: str, document_text: str) -> float:
        """Computes a lightweight keyword match score (0.0 to 1.0) for hybrid ranking."""
        if not query or not document_text:
            return 0.0

        query_terms = set(re.findall(r"\w+", query.lower()))
        doc_terms = re.findall(r"\w+", document_text.lower())

        if not query_terms or not doc_terms:
            return 0.0

        matches = sum(1 for term in doc_terms if term in query_terms)
        score = min(1.0, matches / (math.log(len(doc_terms) + 1) * 2))
        return round(score, 4)

    def generate_embedding_mock(self, text: str) -> List[float]:
        """Legacy helper returning embedding vector."""
        return embedding_service.embed_text(text)


vector_service = VectorService()
