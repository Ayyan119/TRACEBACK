import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.service import ServiceModel
from app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceRepository:
    """Database access repository for Service operations."""

    async def get_all_by_project(self, db: AsyncSession, project_id: str) -> List[ServiceModel]:
        """Fetch all microservices belonging to a specific project_id from PostgreSQL."""
        result = await db.execute(
            select(ServiceModel)
            .where(ServiceModel.project_id == project_id)
            .order_by(ServiceModel.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, service_id: str) -> Optional[ServiceModel]:
        """Fetch a single service by primary key ID."""
        result = await db.execute(select(ServiceModel).where(ServiceModel.id == service_id))
        return result.scalar_one_or_none()

    async def get_by_name_and_project(
        self,
        db: AsyncSession,
        project_id: str,
        name: str,
    ) -> Optional[ServiceModel]:
        """Fetch a single service by name within a specific project."""
        result = await db.execute(
            select(ServiceModel).where(
                ServiceModel.project_id == project_id,
                ServiceModel.name == name,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_name(self, db: AsyncSession, identifier: str) -> Optional[ServiceModel]:
        """Fetch a single service matching either primary key ID or service name."""
        result = await db.execute(
            select(ServiceModel).where(
                or_(ServiceModel.id == identifier, ServiceModel.name == identifier)
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        obj_in: ServiceCreate,
        project_id: str,
    ) -> ServiceModel:
        """Create and persist a new ServiceModel record in PostgreSQL."""
        service_id = str(uuid.uuid4())

        deps_json = [d.model_dump() for d in obj_in.dependencies] if obj_in.dependencies else []
        deps_deployments = [d.model_dump(by_alias=True) for d in obj_in.recent_deployments] if obj_in.recent_deployments else []

        db_obj = ServiceModel(
            id=service_id,
            project_id=project_id,
            name=obj_in.name,
            health="Healthy",
            type=obj_in.type.value if hasattr(obj_in.type, "value") else (obj_in.type or "Backend"),
            description=obj_in.description,
            latency_ms=None,
            error_rate_percent=0.0,
            recent_incidents_count=0,
            dependencies=deps_json,
            recent_deployments=deps_deployments,
            owner_team=obj_in.owner_team,
            repository_url=obj_in.repository_url,
            environment=obj_in.environment or "Production",
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ServiceModel,
        obj_in: ServiceUpdate,
    ) -> ServiceModel:
        """Partially update an existing ServiceModel record in PostgreSQL."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                if hasattr(value, "value"):
                    setattr(db_obj, field, value.value)
                else:
                    setattr(db_obj, field, value)

        db_obj.updated_at = datetime.now(timezone.utc)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ServiceModel) -> None:
        """Delete a ServiceModel record from PostgreSQL."""
        await db.delete(db_obj)
        await db.flush()


service_repository = ServiceRepository()
