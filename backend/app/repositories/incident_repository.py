import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import IncidentModel
from app.schemas.incident import IncidentCreate, IncidentUpdate


class IncidentRepository:
    """Database access repository for Incident operations."""

    async def get_next_code(self, db: AsyncSession) -> str:
        """Generates the next sequential incident code (e.g. INC-1001, INC-1002)."""
        result = await db.execute(select(func.count(IncidentModel.id)))
        count = result.scalar() or 0
        return f"INC-{1001 + count}"

    async def get_all_by_project(
        self,
        db: AsyncSession,
        project_id: str,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[IncidentModel]:
        """Fetch all incidents belonging to a specific project_id with optional severity & status filtering."""
        query = (
            select(IncidentModel)
            .where(IncidentModel.project_id == project_id)
            .order_by(IncidentModel.detected_at.desc())
        )

        if severity:
            query = query.where(IncidentModel.severity == severity)

        if status:
            query = query.where(IncidentModel.status == status)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, incident_id: str) -> Optional[IncidentModel]:
        """Fetch a single incident record by primary key ID."""
        result = await db.execute(select(IncidentModel).where(IncidentModel.id == incident_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[IncidentModel]:
        """Fetch a single incident record by code (e.g. INC-1042)."""
        result = await db.execute(select(IncidentModel).where(IncidentModel.code == code))
        return result.scalar_one_or_none()

    async def get_by_id_or_code(self, db: AsyncSession, identifier: str) -> Optional[IncidentModel]:
        """Fetch a single incident record matching either UUID ID or ticket code."""
        result = await db.execute(
            select(IncidentModel).where(
                or_(IncidentModel.id == identifier, IncidentModel.code == identifier)
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        obj_in: IncidentCreate,
        project_id: str,
        code: str,
    ) -> IncidentModel:
        """Create and persist a new IncidentModel record in PostgreSQL."""
        incident_id = str(uuid.uuid4())
        detected_time = obj_in.detected_at or datetime.now(timezone.utc)

        services_list = obj_in.affected_services or []
        if obj_in.affected_service and obj_in.affected_service not in services_list:
            services_list.insert(0, obj_in.affected_service)

        db_obj = IncidentModel(
            id=incident_id,
            project_id=project_id,
            code=code,
            title=obj_in.title,
            description=obj_in.description,
            severity=obj_in.severity.value if hasattr(obj_in.severity, "value") else str(obj_in.severity or "High"),
            status="Investigating",
            affected_service=obj_in.affected_service or "Backend",
            affected_services=services_list,
            detected_at=detected_time,
            duration="Active",
            confidence=85.0,
            reporter=obj_in.reporter or "SRE On-Call",
            environment=obj_in.environment or "Production",
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: IncidentModel,
        obj_in: IncidentUpdate,
    ) -> IncidentModel:
        """Partially update an existing IncidentModel record in PostgreSQL."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                if hasattr(value, "value"):
                    setattr(db_obj, field, value.value)
                else:
                    setattr(db_obj, field, value)

        if db_obj.status == "Resolved" and not db_obj.resolved_at:
            db_obj.resolved_at = datetime.now(timezone.utc)
            if db_obj.duration == "Active":
                db_obj.duration = "Resolved"

        db_obj.updated_at = datetime.now(timezone.utc)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: IncidentModel) -> None:
        """Delete an IncidentModel record from PostgreSQL using SQL delete statement so CASCADE foreign keys handle child tables."""
        await db.execute(delete(IncidentModel).where(IncidentModel.id == db_obj.id))
        await db.flush()


incident_repository = IncidentRepository()
