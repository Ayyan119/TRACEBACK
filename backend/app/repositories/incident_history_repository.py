import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident_history import IncidentHistoryModel

logger = logging.getLogger(__name__)


class IncidentHistoryRepository:
    """SQLAlchemy 2.0 async repository for IncidentHistoryModel."""

    async def get_by_id(self, db: AsyncSession, history_id: str) -> Optional[IncidentHistoryModel]:
        stmt = select(IncidentHistoryModel).where(IncidentHistoryModel.id == history_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_incident_id(self, db: AsyncSession, incident_id: str) -> Optional[IncidentHistoryModel]:
        stmt = select(IncidentHistoryModel).where(IncidentHistoryModel.incident_id == incident_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_project(self, db: AsyncSession, project_id: str) -> List[IncidentHistoryModel]:
        stmt = (
            select(IncidentHistoryModel)
            .where(IncidentHistoryModel.project_id == project_id)
            .order_by(IncidentHistoryModel.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_or_update(
        self,
        db: AsyncSession,
        incident_id: str,
        project_id: str,
        incident_code: str,
        historical_payload: dict,
        qdrant_point_id: Optional[str] = None,
        status: str = "indexed",
    ) -> IncidentHistoryModel:
        history = await self.get_by_incident_id(db, incident_id)
        if history:
            history.historical_payload = historical_payload
            history.qdrant_point_id = qdrant_point_id or history.qdrant_point_id
            history.status = status
            db.add(history)
        else:
            history = IncidentHistoryModel(
                incident_id=incident_id,
                project_id=project_id,
                incident_code=incident_code,
                historical_payload=historical_payload,
                qdrant_point_id=qdrant_point_id,
                status=status,
            )
            db.add(history)

        await db.flush()
        return history

    async def delete_by_incident_id(self, db: AsyncSession, incident_id: str) -> bool:
        history = await self.get_by_incident_id(db, incident_id)
        if history:
            await db.delete(history)
            await db.flush()
            return True
        return False


incident_history_repository = IncidentHistoryRepository()
