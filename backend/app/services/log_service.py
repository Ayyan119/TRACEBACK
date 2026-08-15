import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log_record import LogRecordModel
from app.repositories.log_repository import log_repository
from app.services.ingestion.log_parser import log_parser

logger = logging.getLogger(__name__)


class LogIngestionService:
    """Service layer orchestrating structured Log storage in PostgreSQL."""

    async def ingest_log_bytes(
        self,
        db: AsyncSession,
        file_bytes: bytes,
        filename: str,
        project_id: str,
        incident_id: Optional[str] = None,
        file_id: Optional[str] = None,
        service: Optional[str] = None,
        log_type: str = "application",
    ) -> List[LogRecordModel]:
        """Parses log bytes and bulk-inserts structured log records into PostgreSQL."""
        if not file_bytes:
            return []

        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = file_bytes.decode("latin-1", errors="replace")

        records = log_parser.parse_log_content(
            content=content,
            project_id=project_id,
            incident_id=incident_id,
            file_id=file_id,
            source=filename,
            service=service,
            log_type=log_type,
        )

        committed_records = await log_repository.create_batch(db, records)
        logger.info(
            f"[LOG-PARSER] Successfully ingested {len(committed_records)} log records "
            f"for project_id={project_id}, file='{filename}'."
        )
        return committed_records

    async def ingest_log_text(
        self,
        db: AsyncSession,
        content: str,
        project_id: str,
        incident_id: Optional[str] = None,
        file_id: Optional[str] = None,
        source: str = "text_snippet",
        service: Optional[str] = None,
        log_type: str = "application",
    ) -> List[LogRecordModel]:
        """Parses raw inline log text and inserts structured log records into PostgreSQL."""
        records = log_parser.parse_log_content(
            content=content,
            project_id=project_id,
            incident_id=incident_id,
            file_id=file_id,
            source=source,
            service=service,
            log_type=log_type,
        )
        return await log_repository.create_batch(db, records)


    async def query_logs(
        self,
        db: AsyncSession,
        project_id: str,
        incident_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        level: Optional[str] = None,
        log_type: Optional[str] = None,
        service: Optional[str] = None,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
        parse_status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LogRecordModel]:
        """Queries structured PostgreSQL log records using flexible filters."""
        return await log_repository.query_logs(
            db=db,
            project_id=project_id,
            incident_id=incident_id,
            start_date=start_date,
            end_date=end_date,
            level=level,
            log_type=log_type,
            service=service,
            source=source,
            keyword=keyword,
            parse_status=parse_status,
            limit=limit,
            offset=offset,
        )


log_service = LogIngestionService()
