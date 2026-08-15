import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investigation import InvestigationModel


class InvestigationRepository:
    """Repository for CRUD operations on InvestigationModel in PostgreSQL."""

    async def get_by_id(self, db: AsyncSession, investigation_id: str) -> Optional[InvestigationModel]:
        """Retrieves single investigation run by ID."""
        stmt = select(InvestigationModel).where(InvestigationModel.id == investigation_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all_by_incident(self, db: AsyncSession, incident_id: str) -> List[InvestigationModel]:
        """Retrieves all investigation runs for an incident ordered by run number desc."""
        stmt = select(InvestigationModel).where(InvestigationModel.incident_id == incident_id).order_by(InvestigationModel.investigation_number.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_next_run_number(self, db: AsyncSession, incident_id: str) -> int:
        """Computes next investigation run number for an incident (max + 1)."""
        stmt = select(func.max(InvestigationModel.investigation_number)).where(InvestigationModel.incident_id == incident_id)
        res = await db.execute(stmt)
        max_num = res.scalar()
        return (max_num or 0) + 1

    async def create(
        self,
        db: AsyncSession,
        incident_id: str,
        project_id: str,
        incident_description: Optional[str] = None,
    ) -> InvestigationModel:
        """Creates a new investigation run record with status CREATED."""
        next_num = await self.get_next_run_number(db, incident_id)
        record = InvestigationModel(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            project_id=project_id,
            investigation_number=next_num,
            status="CREATED",
            started_at=datetime.now(timezone.utc),
            incident_description=incident_description,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def mark_running(self, db: AsyncSession, investigation_id: str) -> Optional[InvestigationModel]:
        """Transitions investigation run status to RUNNING."""
        record = await self.get_by_id(db, investigation_id)
        if record:
            record.status = "RUNNING"
            record.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(record)
        return record

    async def mark_completed(
        self,
        db: AsyncSession,
        investigation_id: str,
        result_data: Dict[str, Any],
        duration_ms: Optional[float] = None,
    ) -> Optional[InvestigationModel]:
        """Transitions investigation run status to COMPLETED and persists final RCA result."""
        record = await self.get_by_id(db, investigation_id)
        if record:
            now = datetime.now(timezone.utc)
            record.status = "COMPLETED"
            record.completed_at = now
            if duration_ms is not None:
                record.duration_ms = duration_ms
            elif record.started_at:
                st = record.started_at.replace(tzinfo=timezone.utc) if record.started_at.tzinfo is None else record.started_at
                record.duration_ms = (now - st).total_seconds() * 1000.0

            record.final_summary = result_data.get("investigation_summary")
            record.confidence = result_data.get("confidence")

            selected = result_data.get("selected_hypothesis")
            if selected:
                record.selected_hypothesis_json = selected
                record.root_cause = selected.get("title") or selected.get("likely_root_cause")

            record.final_report_json = result_data.get("final_report")
            record.hypotheses_json = result_data.get("hypotheses")
            record.accepted_evidence_json = result_data.get("accepted_evidence")
            record.rejected_evidence_json = result_data.get("rejected_evidence")
            record.execution_trace_json = result_data.get("execution_trace")
            record.updated_at = now

            await db.commit()
            await db.refresh(record)
        return record

    async def mark_failed(
        self,
        db: AsyncSession,
        investigation_id: str,
        error_message: str,
    ) -> Optional[InvestigationModel]:
        """Transitions investigation run status to FAILED and persists sanitized error message."""
        record = await self.get_by_id(db, investigation_id)
        if record:
            now = datetime.now(timezone.utc)
            record.status = "FAILED"
            record.completed_at = now
            if record.started_at:
                st = record.started_at.replace(tzinfo=timezone.utc) if record.started_at.tzinfo is None else record.started_at
                record.duration_ms = (now - st).total_seconds() * 1000.0
            record.error_message = error_message
            record.updated_at = now

            await db.commit()
            await db.refresh(record)
        return record


investigation_repository = InvestigationRepository()
