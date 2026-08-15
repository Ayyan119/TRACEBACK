import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class EnrichedChunk:
    chunk_id: str
    document_id: str
    chunk_index: int
    original_content: str
    embedding_text: str
    checksum: str
    content_length: int
    page: Optional[int] = None
    slide: Optional[int] = None
    section: Optional[str] = None
    file_name: str = ""
    file_type: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextEnricher:
    """Enriches raw document chunks with structural context while retaining original_content intact."""

    def enrich_chunk(
        self,
        document_id: str,
        chunk_index: int,
        original_content: str,
        file_name: str,
        file_type: str,
        section: Optional[str] = None,
        page: Optional[int] = None,
        slide: Optional[int] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> EnrichedChunk:
        # Deterministic SHA256 Chunk ID
        unique_str = f"{document_id}_{chunk_index}_{original_content}"
        chunk_id = hashlib.sha256(unique_str.encode("utf-8")).hexdigest()

        checksum = hashlib.sha256(original_content.encode("utf-8")).hexdigest()

        # Construct enriched embedding text string
        header_lines = [
            f"Document: {file_name}",
            f"File type: {file_type}",
        ]
        if section:
            header_lines.append(f"Section: {section}")
        if page:
            header_lines.append(f"Page: {page}")
        if slide:
            header_lines.append(f"Slide: {slide}")

        embedding_text = "\n".join(header_lines) + f"\n\nContent:\n{original_content}"

        meta = extra_metadata or {}
        meta.update(
            {
                "document_id": document_id,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "file_name": file_name,
                "file_type": file_type,
                "section": section,
                "page": page,
                "slide": slide,
                "checksum": checksum,
                "content_length": len(original_content),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        return EnrichedChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            chunk_index=chunk_index,
            original_content=original_content,
            embedding_text=embedding_text,
            checksum=checksum,
            content_length=len(original_content),
            page=page,
            slide=slide,
            section=section,
            file_name=file_name,
            file_type=file_type,
            metadata=meta,
        )


context_enricher = ContextEnricher()
