import logging
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from qdrant_client.http import models as qmodels

from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.ingestion.chunker import chunker
from app.services.ingestion.context_enricher import context_enricher
from app.services.ingestion.structure_detector import structure_detector
from app.services.ingestion.universal_loader import universal_loader
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """End-to-End Production Document Ingestion & Vector Indexing Orchestrator for TRACEBACK."""

    def ingest_knowledge_document(
        self,
        file_bytes: bytes,
        filename: str,
        project_id: str,
        knowledge_document_id: str,
        category: str = "General",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Tuple[str, int, List[Dict[str, Any]], str]:
        """Runs the complete Knowledge Document Ingestion Architecture:

        Loader -> Structure -> Chunker -> Context Enrichment -> Validation -> Embedding -> Qdrant
        """
        start_time = datetime.now(timezone.utc)

        # 1. Document Checksum calculation
        doc_checksum = hashlib.sha256(file_bytes).hexdigest()

        # 2. Universal Document Loader
        loaded_doc = universal_loader.load_document(
            file_bytes=file_bytes,
            filename=filename,
            document_id=knowledge_document_id,
        )

        all_enriched_chunks = []
        full_extracted_text_blocks = []

        # 3. Process each loaded element through Structure Detection & LangChain Chunker
        for elem in loaded_doc.elements:
            full_extracted_text_blocks.append(elem.content)
            # Detect Structure
            structures = structure_detector.detect_structure(elem.content)

            for struct in structures:
                sect_title = struct["section"] or elem.section or "General"
                sub_text = struct["text"]

                # LangChain RecursiveCharacterTextSplitter Chunker
                t_chunks = chunker.chunk_text(
                    text=sub_text,
                    chunk_size=chunk_size or getattr(settings, "CHUNK_SIZE", 3000),
                    chunk_overlap=chunk_overlap or getattr(settings, "CHUNK_OVERLAP", 300),
                )

                for tc in t_chunks:
                    # Context Enrichment: Create BOTH original_content and embedding_text
                    enriched = context_enricher.enrich_chunk(
                        document_id=knowledge_document_id,
                        chunk_index=len(all_enriched_chunks),
                        original_content=tc.text,
                        file_name=filename,
                        file_type=loaded_doc.file_type,
                        section=sect_title,
                        page=elem.page,
                        slide=elem.slide,
                        extra_metadata={
                            "project_id": project_id,
                            "knowledge_document_id": knowledge_document_id,
                            "category": category,
                            "doc_checksum": doc_checksum,
                        },
                    )
                    all_enriched_chunks.append(enriched)

        total_chunks = len(all_enriched_chunks)
        full_text = "\n\n".join(full_extracted_text_blocks)

        if total_chunks == 0:
            return full_text, 0, [], doc_checksum

        # 4. Generate Embeddings for embedding_text
        embedding_inputs = [c.embedding_text for c in all_enriched_chunks]
        embeddings = embedding_service.embed_documents(embedding_inputs)
        dimension = embedding_service.embedding_dim

        # 5. Ensure Qdrant collection matches dimension
        vector_store.ensure_collection(dimension=dimension)

        # 6. Idempotent Re-indexing: Remove previous points for this document
        vector_store.delete_source_vectors(source_type="knowledge", source_id=knowledge_document_id)

        # 7. Create Qdrant PointStruct objects with full payload
        points: List[qmodels.PointStruct] = []
        payload_summaries: List[Dict[str, Any]] = []

        for c, emb in zip(all_enriched_chunks, embeddings):
            payload = {
                "project_id": project_id,
                "knowledge_document_id": knowledge_document_id,
                "document_id": knowledge_document_id,
                "source_type": "knowledge",
                "source_id": knowledge_document_id,
                "chunk_id": c.chunk_id,
                "file_name": c.file_name,
                "file_type": c.file_type,
                "section": c.section,
                "page": c.page,
                "slide": c.slide,
                "chunk_index": c.chunk_index,
                "total_chunks": total_chunks,
                "original_content": c.original_content,
                "embedding_text": c.embedding_text,
                "text": c.original_content,
                "content_length": c.content_length,
                "checksum": c.checksum,
                "doc_checksum": doc_checksum,
                "category": category,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Qdrant Point ID: Deterministic UUID or Hex Hash
            point_id = c.chunk_id[:32]
            # Convert 32-char hex string to UUID format if needed
            formatted_uuid = f"{point_id[:8]}-{point_id[8:12]}-{point_id[12:16]}-{point_id[16:20]}-{point_id[20:32]}"

            points.append(
                qmodels.PointStruct(
                    id=formatted_uuid,
                    vector=emb,
                    payload=payload,
                )
            )
            payload_summaries.append(payload)

        # 8. Upsert Vectors into Qdrant
        vector_store.upsert_chunks(points)

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            f"[INGESTION] Knowledge doc '{filename}' (ID: {knowledge_document_id}) processed successfully! "
            f"Indexed {total_chunks} chunks into Qdrant in {duration:.3f}s."
        )

        return full_text, total_chunks, payload_summaries, doc_checksum

    def ingest_file(
        self,
        file_bytes: bytes,
        filename: str,
        project_id: str,
        source_type: str,
        source_id: str,
        category_or_type: str = "General",
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Tuple[str, int, List[Dict[str, Any]]]:
        """Backward compatible alias for knowledge document ingestion."""
        text, total_chunks, payload_summaries, _ = self.ingest_knowledge_document(
            file_bytes=file_bytes,
            filename=filename,
            project_id=project_id,
            knowledge_document_id=source_id,
            category=category_or_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return text, total_chunks, payload_summaries

    def ingest_text_snippet(
        self,
        content: str,
        title: str,
        project_id: str,
        source_type: str,
        source_id: str,
        category_or_type: str = "Snippet",
    ) -> Tuple[str, int, List[Dict[str, Any]], str]:
        """Ingests raw text snippet as a document into the pipeline."""
        encoded_bytes = content.encode("utf-8")
        return self.ingest_knowledge_document(
            file_bytes=encoded_bytes,
            filename=f"{title}.md",
            project_id=project_id,
            knowledge_document_id=source_id,
            category=category_or_type,
        )


document_ingestion_service = DocumentIngestionService()
