import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evidence import EvidenceModel
from app.schemas.evidence import EvidenceCreate


class EvidenceRepository:
    """Database access repository for Evidence operations."""

    async def get_all_by_incident(
        self,
        db: AsyncSession,
        incident_id: str,
        evidence_type: Optional[str] = None,
    ) -> List[EvidenceModel]:
        """Fetch all evidence items for an incident ordered by created_at DESC."""
        query = (
            select(EvidenceModel)
            .where(EvidenceModel.incident_id == incident_id)
            .order_by(EvidenceModel.created_at.desc())
        )
        if evidence_type:
            query = query.where(EvidenceModel.type == evidence_type)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, evidence_id: str) -> Optional[EvidenceModel]:
        """Fetch a single evidence item by ID."""
        result = await db.execute(select(EvidenceModel).where(EvidenceModel.id == evidence_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        incident_id: str,
        type_str: str,
        title: str,
        source: str,
        file_url: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        raw_content: Optional[str] = None,
        metadata_dict: Optional[dict] = None,
    ) -> EvidenceModel:
        """Create and persist an EvidenceModel in PostgreSQL."""
        db_obj = EvidenceModel(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            type=type_str,
            title=title,
            source=source,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            status="ready",
            raw_content=raw_content,
            metadata_json=metadata_dict or {},
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: EvidenceModel) -> None:
        """Delete an evidence item from PostgreSQL."""
        await db.delete(db_obj)
        await db.flush()


evidence_repository = EvidenceRepository()
