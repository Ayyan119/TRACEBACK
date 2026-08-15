import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log_record import LogRecordModel

logger = logging.getLogger(__name__)


class LogRepository:
    """Repository layer for structured LogRecordModel operations."""

    async def create_batch(
        self,
        db: AsyncSession,
        records: List[LogRecordModel],
    ) -> List[LogRecordModel]:
        """Bulk insert structured log records into PostgreSQL."""
        if not records:
            return []
        db.add_all(records)
        await db.commit()
        logger.info(f"Successfully committed {len(records)} structured log records to PostgreSQL.")
        return records

    async def query_logs(
        self,
        db: AsyncSession,
        project_id: str,
        incident_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        level: Optional[str] = None,
        log_type: Optional[str] = None,
        service: Optional[str] = None,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
        parse_status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LogRecordModel]:
        """Queries structured log records with project isolation and flexible filter criteria."""
        stmt = select(LogRecordModel).where(LogRecordModel.project_id == project_id)

        if incident_id:
            stmt = stmt.where(LogRecordModel.incident_id == incident_id)
        if level:
            stmt = stmt.where(LogRecordModel.level == level.upper())
        if log_type:
            stmt = stmt.where(LogRecordModel.log_type == log_type)
        if service:
            stmt = stmt.where(LogRecordModel.service == service)
        if source:
            stmt = stmt.where(LogRecordModel.source == source)
        if parse_status:
            stmt = stmt.where(LogRecordModel.parse_status == parse_status)
        if start_date:
            stmt = stmt.where(LogRecordModel.date >= start_date)
        if end_date:
            stmt = stmt.where(LogRecordModel.date <= end_date)
        if keyword:
            stmt = stmt.where(
                LogRecordModel.message.ilike(f"%{keyword}%") | LogRecordModel.raw_line.ilike(f"%{keyword}%")
            )

        stmt = stmt.order_by(LogRecordModel.timestamp.desc()).offset(offset).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_all_by_incident(self, db: AsyncSession, incident_id: str) -> List[LogRecordModel]:
        """Fetch all structured log records associated with a specific incident ID."""
        stmt = select(LogRecordModel).where(LogRecordModel.incident_id == incident_id).order_by(LogRecordModel.timestamp.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())


log_repository = LogRepository()
