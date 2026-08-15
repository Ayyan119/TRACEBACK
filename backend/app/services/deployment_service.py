from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.deployment import DeploymentModel
from app.repositories.deployment_repository import deployment_repository
from app.schemas.deployment import DeploymentCreate
from app.services.project_service import project_service
from app.services.service_service import service_service


class DeploymentService:
    """Business logic service for Deployment operations."""

    async def get_deployments_by_service(
        self,
        db: AsyncSession,
        service_id: str,
    ) -> List[DeploymentModel]:
        """Retrieves deployment history for a target service ordered by deployed_at desc."""
        service = await service_service.get_service_by_id(db, service_id)
        return await deployment_repository.get_all_by_service(db, service.id)

    async def get_deployments_by_project(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> List[DeploymentModel]:
        """Retrieves system-wide deployment change timeline across all services in a project workspace."""
        project = await project_service.get_project_by_id(db, project_id)
        return await deployment_repository.get_all_by_project(db, project.id)

    async def create_deployment(
        self,
        db: AsyncSession,
        service_id: str,
        obj_in: DeploymentCreate,
    ) -> DeploymentModel:
        """Validates service existence and creates a new deployment event record in PostgreSQL."""
        service = await service_service.get_service_by_id(db, service_id)

        new_deployment = await deployment_repository.create(
            db=db,
            obj_in=obj_in,
            service_id=service.id,
            project_id=service.project_id,
        )

        recent = list(service.recent_deployments or [])
        recent_entry = {
            "id": new_deployment.id,
            "version": new_deployment.version,
            "deployedAt": new_deployment.deployed_at.isoformat(),
            "author": new_deployment.author,
        }
        recent.insert(0, recent_entry)
        service.recent_deployments = recent[:10]
        db.add(service)
        await db.flush()

        return new_deployment


deployment_service = DeploymentService()
