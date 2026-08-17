import os
import logging
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceNotFoundException
from app.models.knowledge import KnowledgeDocumentModel
from app.repositories.knowledge_repository import knowledge_repository
from app.schemas.knowledge import KnowledgeDocumentCreate
from app.services.ingestion.ingestion_service import document_ingestion_service
from app.services.log_service import log_service
from app.services.project_service import project_service
from app.services.storage_service import storage_service
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Business logic service for Knowledge Base operations with pipeline routing."""

    async def get_documents_by_project(
        self,
        db: AsyncSession,
        project_id: str,
        category: Optional[str] = None,
    ) -> List[KnowledgeDocumentModel]:
        """Fetch all knowledge documents for a workspace project, validating project existence and syncing incidents."""
        project = await project_service.get_project_by_id(db, project_id)

        # Auto-sync project incidents into Knowledge Base Catalog
        try:
            from app.repositories.incident_repository import incident_repository
            from app.services.incident_history_service import incident_history_service

            incidents = await incident_repository.get_all_by_project(db, project.id)
            for inc in incidents:
                await incident_history_service.index_incident_history(db, inc)
        except Exception as sync_err:
            logger.warning(f"Failed to auto-sync project incidents into knowledge documents: {sync_err}")

        return await knowledge_repository.get_all_by_project(db, project.id, category=category)

    async def create_document(
        self,
        db: AsyncSession,
        project_id: str,
        obj_in: KnowledgeDocumentCreate,
    ) -> KnowledgeDocumentModel:
        """Creates a knowledge document from JSON text payload and indexes it into Qdrant."""
        project = await project_service.get_project_by_id(db, project_id)

        file_url = None
        file_size = None
        mime_type = None

        if obj_in.content:
            file_url, file_size, mime_type = storage_service.save_raw_text_snippet(obj_in.content, extension=".md")

        doc = await knowledge_repository.create(
            db=db,
            project_id=project.id,
            title=obj_in.title,
            category=obj_in.category or "Architecture",
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            content=obj_in.content,
            chunk_count=0,
            metadata_dict=obj_in.metadata_json or {},
        )

        # Run vector ingestion pipeline for text snippets
        try:
            if obj_in.content:
                extracted_text, total_chunks, _, checksum = document_ingestion_service.ingest_text_snippet(
                    content=obj_in.content,
                    title=obj_in.title,
                    project_id=project.id,
                    source_type="knowledge",
                    source_id=doc.id,
                    category_or_type=doc.category,
                )
                doc.status = "indexed"
                doc.chunk_count = total_chunks
                doc.content = extracted_text
                doc.checksum = checksum
                await db.commit()
                await db.refresh(doc)
        except Exception as e:
            logger.error(f"Vector indexing failed for knowledge snippet document {doc.id}: {e}")
            doc.status = "failed"
            await db.commit()
            raise e

        return doc

    async def upload_document_file(
        self,
        db: AsyncSession,
        project_id: str,
        category: str,
        title: str,
        file: UploadFile,
    ) -> KnowledgeDocumentModel:
        """Uploads a knowledge file, routing logs to PostgreSQL structured log table, and documents to Qdrant vector pipeline."""
        project = await project_service.get_project_by_id(db, project_id)

        file_url, file_size, mime_type = await storage_service.save_upload_file(file)

        await file.seek(0)
        file_bytes = await file.read()

        doc_title = title or file.filename or "Uploaded Document"
        doc_category = category or "Architecture"
        file_ext = os.path.splitext(file.filename or "")[1].lower()

        # 1. Create initial PostgreSQL Knowledge Document Record
        doc = await knowledge_repository.create(
            db=db,
            project_id=project.id,
            title=doc_title,
            category=doc_category,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            content=None,
            chunk_count=0,
            metadata_dict={"original_filename": file.filename},
        )
        doc.status = "processing"
        await db.commit()

        # 2. ROUTING: KNOWLEDGE LOGS vs KNOWLEDGE DOCUMENTS
        if file_ext == ".log" or (mime_type and "log" in mime_type):
            logger.info(f"[ROUTING] Knowledge Log file detected: '{file.filename}'. Routing to PostgreSQL log_records.")
            try:
                log_records = await log_service.ingest_log_bytes(
                    db=db,
                    file_bytes=file_bytes,
                    filename=file.filename or doc_title,
                    project_id=project.id,
                    file_id=doc.id,
                    service="KnowledgeLog",
                    log_type="knowledge_log",
                )
                doc.status = "indexed"
                doc.chunk_count = len(log_records)
                doc.content = f"Parsed {len(log_records)} structured log records into PostgreSQL log_records table."
                await db.commit()
                await db.refresh(doc)
            except Exception as e:
                logger.error(f"Knowledge log processing failed for '{file.filename}': {e}")
                doc.status = "failed"
                await db.commit()
                raise e
            return doc

        # 3. KNOWLEDGE DOCUMENT PIPELINE
        try:
            extracted_text, total_chunks, _, checksum = document_ingestion_service.ingest_knowledge_document(
                file_bytes=file_bytes,
                filename=file.filename or doc_title,
                project_id=project.id,
                knowledge_document_id=doc.id,
                category=doc_category,
            )
            doc.status = "indexed"
            doc.chunk_count = total_chunks
            doc.content = extracted_text[:10000]
            doc.checksum = checksum
            await db.commit()
            await db.refresh(doc)
        except Exception as e:
            logger.error(f"Knowledge document vector ingestion failed for '{file.filename}' (ID: {doc.id}): {e}")
            doc.status = "failed"
            await db.commit()
            raise e

        return doc

    async def delete_document(
        self,
        db: AsyncSession,
        document_id: str,
    ) -> None:
        """Deletes a knowledge document from PostgreSQL and disassociates its vectors from Qdrant."""
        doc = await knowledge_repository.get_by_id(db, document_id)
        if not doc:
            raise ResourceNotFoundException("Knowledge Document", document_id)

        vector_store.delete_source_vectors(source_type="knowledge", source_id=doc.id)
        await knowledge_repository.delete(db, doc)


knowledge_service = KnowledgeService()
