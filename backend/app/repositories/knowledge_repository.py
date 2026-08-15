import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import KnowledgeDocumentModel


class KnowledgeRepository:
    """Database access repository for Knowledge Base operations."""

    async def get_all_by_project(
        self,
        db: AsyncSession,
        project_id: str,
        category: Optional[str] = None,
    ) -> List[KnowledgeDocumentModel]:
        """Fetch all knowledge documents for a workspace project ordered by created_at DESC."""
        query = (
            select(KnowledgeDocumentModel)
            .where(KnowledgeDocumentModel.project_id == project_id)
            .order_by(KnowledgeDocumentModel.created_at.desc())
        )
        if category:
            query = query.where(KnowledgeDocumentModel.category == category)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, document_id: str) -> Optional[KnowledgeDocumentModel]:
        """Fetch a single knowledge document by ID."""
        result = await db.execute(select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.id == document_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        project_id: str,
        title: str,
        category: str,
        file_url: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        content: Optional[str] = None,
        chunk_count: int = 1,
        metadata_dict: Optional[dict] = None,
    ) -> KnowledgeDocumentModel:
        """Create and persist a KnowledgeDocumentModel in PostgreSQL."""
        db_obj = KnowledgeDocumentModel(
            id=str(uuid.uuid4()),
            project_id=project_id,
            title=title,
            category=category,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            status="ready",
            chunk_count=chunk_count,
            content=content,
            metadata_json=metadata_dict or {},
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: KnowledgeDocumentModel) -> None:
        """Delete a knowledge document from PostgreSQL."""
        await db.delete(db_obj)
        await db.flush()


knowledge_repository = KnowledgeRepository()
