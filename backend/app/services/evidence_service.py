import os
import logging
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceNotFoundException
from app.models.evidence import EvidenceModel
from app.repositories.evidence_repository import evidence_repository
from app.schemas.evidence import EvidenceCreate
from app.services.incident_service import incident_service
from app.services.llm_summarizer import llm_summarizer
from app.services.log_service import log_service
from app.services.storage_service import storage_service
from app.services.vector_store import vector_store
from app.services.ingestion.universal_loader import universal_loader
from app.services.ingestion.file_extractor import IngestionError

logger = logging.getLogger(__name__)


class EvidenceService:
    """Business logic service for Incident Evidence Operations with 4-way pipeline routing."""

    async def get_evidence_by_incident(
        self,
        db: AsyncSession,
        incident_id: str,
        evidence_type: Optional[str] = None,
    ) -> List[EvidenceModel]:
        """Fetch all evidence items for an incident, validating incident existence."""
        incident = await incident_service.get_incident_by_id(db, incident_id)
        return await evidence_repository.get_all_by_incident(db, incident.id, evidence_type=evidence_type)

    async def create_evidence(
        self,
        db: AsyncSession,
        incident_id: str,
        obj_in: EvidenceCreate,
    ) -> EvidenceModel:
        """Creates an evidence item from JSON payload (e.g. stack trace, terminal output)."""
        incident = await incident_service.get_incident_by_id(db, incident_id)

        file_url = None
        file_size = None
        mime_type = None

        if obj_in.raw_content:
            file_url, file_size, mime_type = storage_service.save_raw_text_snippet(obj_in.raw_content)

        type_str = obj_in.type.value if hasattr(obj_in.type, "value") else str(obj_in.type)

        ev = await evidence_repository.create(
            db=db,
            incident_id=incident.id,
            type_str=type_str,
            title=obj_in.title,
            source=obj_in.source,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            raw_content=obj_in.raw_content,  # Exact stack trace / text retained without over-normalization
            metadata_dict=obj_in.metadata_json or {},
        )
        ev.status = "ready"
        await db.commit()
        return ev

    async def upload_evidence_file(
        self,
        db: AsyncSession,
        incident_id: str,
        type_str: str,
        title: str,
        source: str,
        file: UploadFile,
        is_mandatory_log: bool = False,
    ) -> EvidenceModel:
        """Uploads an evidence file, executing 4-way incident evidence routing:

        1. IMAGE -> Preserve original image file, evidence_type="image" (no chunking, no text conversion).
        2. LOG -> Parse into structured PostgreSQL log_records table.
        3. DOCUMENT -> UniversalLoader -> LLM Summarizer -> Store summary as evidence + preserve original file.
        4. STACK TRACE / TEXT -> Retain exact original text.
        """
        incident = await incident_service.get_incident_by_id(db, incident_id)

        # Enforce max 10 evidence attachments limit (excluding mandatory log file)
        await self._validate_evidence_attachment_limit(db, incident.id, type_str, source, title, is_mandatory_log)

        file_url, file_size, mime_type = await storage_service.save_upload_file(file)

        await file.seek(0)
        file_bytes = await file.read()

        file_ext = os.path.splitext(file.filename or "")[1].lower()

        # ROUTE 1: INCIDENT IMAGE PIPELINE
        if (mime_type and "image/" in mime_type) or file_ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            logger.info(f"[INCIDENT-IMAGE] Preserving original image '{file.filename}' for vision LLM input.")
            ev = await evidence_repository.create(
                db=db,
                incident_id=incident.id,
                type_str="image",
                title=title or file.filename or "Incident Image Evidence",
                source=source or "User Upload",
                file_url=file_url,
                file_size=file_size,
                mime_type=mime_type or "image/png",
                raw_content=None,  # Binary image content NOT converted to text
                metadata_dict={"original_filename": file.filename, "file_url": file_url},
            )
            ev.status = "ready"
            await db.commit()
            return ev

        # ROUTE 2: INCIDENT LOG PIPELINE
        if file_ext == ".log" or (mime_type and "log" in mime_type):
            logger.info(f"[INCIDENT-LOG] Parsing log file '{file.filename}' into PostgreSQL log_records.")
            ev = await evidence_repository.create(
                db=db,
                incident_id=incident.id,
                type_str="log",
                title=title or file.filename or "Incident Log File",
                source=source or "Log Collector",
                file_url=file_url,
                file_size=file_size,
                mime_type=mime_type or "text/plain",
                raw_content=None,
                metadata_dict={"original_filename": file.filename},
            )
            try:
                log_records = await log_service.ingest_log_bytes(
                    db=db,
                    file_bytes=file_bytes,
                    filename=file.filename or title,
                    project_id=incident.project_id,
                    incident_id=incident.id,
                    file_id=ev.id,
                    service=source or "IncidentService",
                    log_type="incident_log",
                )
                ev.status = "ready"
                ev.raw_content = f"Parsed {len(log_records)} structured log records into PostgreSQL log_records."
                await db.commit()
                await db.refresh(ev)
            except Exception as e:
                logger.error(f"Incident log parsing failed for '{file.filename}': {e}")
                ev.status = "ready"
                await db.commit()

            return ev

        # ROUTE 3: INCIDENT DOCUMENT PIPELINE (Extract -> LLM Summarize -> Evidence)
        if file_ext in [".pdf", ".docx", ".pptx", ".txt", ".md", ".json", ".csv"]:
            logger.info(f"[INCIDENT-DOCUMENT] Extracting & Summarizing document '{file.filename}'.")
            # Enforce 3-page limit for incident evidence documents
            self._validate_document_page_limit(file_bytes, file.filename or title)

            try:
                loaded_doc = universal_loader.load_document(file_bytes, file.filename or title, document_id=file.filename)
                extracted_text = "\n\n".join([el.content for el in loaded_doc.elements])
                summary = llm_summarizer.summarize_incident_text(extracted_text, filename=file.filename or title)

                ev = await evidence_repository.create(
                    db=db,
                    incident_id=incident.id,
                    type_str="document",
                    title=title or file.filename or "Incident Document Evidence",
                    source=source or "User Upload",
                    file_url=file_url,
                    file_size=file_size,
                    mime_type=mime_type or "application/octet-stream",
                    raw_content=summary,  # Store AI summary as evidence
                    metadata_dict={"original_filename": file.filename, "file_url": file_url},
                )
                ev.status = "ready"
                return ev
            except Exception as e:
                logger.error(f"Incident document processing warning for '{file.filename}': {e}")
                raise e
        # ROUTE 4: DEFAULT TEXT / STACKTRACE FALLBACK
        ev = await evidence_repository.create(
            db=db,
            incident_id=incident.id,
            type_str=type_str or "text",
            title=title or file.filename or "Incident Text Evidence",
            source=source or "User Upload",
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            raw_content=file_bytes.decode("utf-8", errors="replace"),
            metadata_dict={"original_filename": file.filename},
        )
        ev.status = "ready"
        await db.commit()
        return ev

    def _validate_document_page_limit(self, file_bytes: bytes, filename: str) -> None:
        """Enforces strict maximum 3-page / 3-slide limit for incident evidence documents."""
        file_ext = os.path.splitext(filename or "")[1].lower()

        if file_ext == ".pdf":
            try:
                import pypdf, io
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                page_count = len(reader.pages)
                if page_count > 3:
                    raise IngestionError(
                        "PAGE_LIMIT_EXCEEDED",
                        f"PDF document '{filename}' exceeds maximum 3-page limit ({page_count} pages). "
                        f"Incident evidence documents must be 3 pages or fewer.",
                    )
            except IngestionError:
                raise
            except Exception:
                pass

        elif file_ext == ".pptx":
            try:
                import pptx, io
                prs = pptx.Presentation(io.BytesIO(file_bytes))
                slide_count = len(prs.slides)
                if slide_count > 3:
                    raise IngestionError(
                        "PAGE_LIMIT_EXCEEDED",
                        f"Presentation '{filename}' exceeds maximum 3-slide limit ({slide_count} slides). "
                        f"Incident evidence documents must be 3 pages or fewer.",
                    )
            except IngestionError:
                raise
            except Exception:
                pass

        elif file_ext in [".docx", ".txt", ".md", ".json", ".csv"]:
            # Character limit equivalent to 3 standard pages (~9,000 characters)
            text_len = len(file_bytes.decode("utf-8", errors="replace"))
            if text_len > 9000:
                raise IngestionError(
                    "PAGE_LIMIT_EXCEEDED",
                    f"Document '{filename}' exceeds maximum 3-page content limit (~9,000 characters). "
                    f"Incident evidence documents must be 3 pages or fewer.",
                )

    async def _validate_evidence_attachment_limit(
        self,
        db: AsyncSession,
        incident_id: str,
        type_str: str,
        source: Optional[str] = None,
        title: Optional[str] = None,
        is_mandatory_log: bool = False,
    ) -> None:
        """Enforces maximum 10 evidence attachments limit per incident.
        The required incident log file is separate and does NOT count toward this limit.
        """
        if is_mandatory_log or source == "Incident Creation" or (title and title.startswith("Mandatory Log")):
            return

        existing_items = await evidence_repository.get_all_by_incident(db, incident_id)
        evidence_attachments = [
            ev for ev in existing_items
            if not (ev.source == "Incident Creation" or (ev.title and ev.title.startswith("Mandatory Log")))
        ]

        if len(evidence_attachments) >= 10:
            raise IngestionError(
                "EVIDENCE_LIMIT_EXCEEDED",
                "Maximum 10 evidence files allowed. The incident log is separate and does not count toward this limit.",
            )

    async def delete_evidence(
        self,
        db: AsyncSession,
        evidence_id: str,
    ) -> None:
        """Deletes an evidence item by ID and disassociates its vectors from Qdrant."""
        ev = await evidence_repository.get_by_id(db, evidence_id)
        if not ev:
            raise ResourceNotFoundException("Evidence", evidence_id)

        vector_store.delete_source_vectors(source_type="evidence", source_id=ev.id)
        await evidence_repository.delete(db, ev)


evidence_service = EvidenceService()
