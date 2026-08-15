import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deployment import DeploymentModel
from app.schemas.deployment import DeploymentCreate, DeploymentUpdate


class DeploymentRepository:
    """Database access repository for Deployment operations."""

    async def get_by_id(self, db: AsyncSession, deployment_id: str) -> Optional[DeploymentModel]:
        """Fetch a single deployment record by primary key ID."""
        result = await db.execute(select(DeploymentModel).where(DeploymentModel.id == deployment_id))
        return result.scalar_one_or_none()

    async def get_all_by_service(self, db: AsyncSession, service_id: str) -> List[DeploymentModel]:
        """Fetch all deployment records for a specific service_id ordered by deployed_at desc."""
        result = await db.execute(
            select(DeploymentModel)
            .where(DeploymentModel.service_id == service_id)
            .order_by(DeploymentModel.deployed_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_by_project(self, db: AsyncSession, project_id: str) -> List[DeploymentModel]:
        """Fetch all deployment records for a specific project_id ordered by deployed_at desc."""
        result = await db.execute(
            select(DeploymentModel)
            .where(DeploymentModel.project_id == project_id)
            .order_by(DeploymentModel.deployed_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        db: AsyncSession,
        obj_in: DeploymentCreate,
        service_id: str,
        project_id: str,
    ) -> DeploymentModel:
        """Create and persist a new DeploymentModel record in PostgreSQL."""
        deployment_id = str(uuid.uuid4())
        deployed_at_time = obj_in.deployed_at or datetime.now(timezone.utc)

        db_obj = DeploymentModel(
            id=deployment_id,
            project_id=project_id,
            service_id=service_id,
            version=obj_in.version,
            commit_hash=obj_in.commit_hash,
            author=obj_in.author or "CI/CD Pipeline",
            deployed_at=deployed_at_time,
            environment=obj_in.environment or "Production",
            status=obj_in.status.value if hasattr(obj_in.status, "value") else str(obj_in.status or "Success"),
            summary=obj_in.summary,
            config_changes=obj_in.config_changes,
            diff_summary=obj_in.diff_summary,
            pr_url=obj_in.pr_url,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


deployment_repository = DeploymentRepository()
