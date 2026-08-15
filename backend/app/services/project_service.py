import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.project import ProjectModel
from app.repositories.project_repository import project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Business logic service for Project operations."""

    def generate_slug(self, name: str) -> str:
        """Helper to convert project name to URL-safe slug."""
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_-]+", "-", slug)
        return slug

    async def get_projects(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> List[ProjectModel]:
        """Retrieves list of workspace projects with optional filters."""
        return await project_repository.get_all(db, search=search, environment=environment)

    async def get_project_by_id(self, db: AsyncSession, project_id: str) -> ProjectModel:
        """Retrieves a single project by ID or slug, or raises 404 ResourceNotFoundException."""
        project = await project_repository.get_by_id_or_slug(db, project_id)
        if not project:
            raise ResourceNotFoundException("Project", project_id)
        return project

    async def create_project(self, db: AsyncSession, obj_in: ProjectCreate) -> ProjectModel:
        """Validates business rules and creates a new project workspace."""
        slug = obj_in.slug if obj_in.slug else self.generate_slug(obj_in.name)

        existing = await project_repository.get_by_slug(db, slug)
        if existing:
            raise BadRequestException(f"Project with slug '{slug}' already exists.")

        return await project_repository.create(db, obj_in, slug)

    async def update_project(
        self,
        db: AsyncSession,
        project_id: str,
        obj_in: ProjectUpdate,
    ) -> ProjectModel:
        """Updates project properties partially or raises 404."""
        project = await self.get_project_by_id(db, project_id)
        return await project_repository.update(db, project, obj_in)

    async def delete_project(self, db: AsyncSession, project_id: str) -> None:
        """Deletes a workspace project and its isolated resources or raises 404."""
        project = await self.get_project_by_id(db, project_id)
        await project_repository.delete(db, project)

    async def export_project(self, db: AsyncSession, project_id: str) -> dict:
        """Generates export data report dictionary for a project."""
        from datetime import datetime, timezone
        from app.repositories.service_repository import service_repository
        from app.repositories.incident_repository import incident_repository
        from app.repositories.knowledge_repository import knowledge_repository
        from app.schemas.project import ProjectResponse
        from app.schemas.service import ServiceResponse
        from app.schemas.incident import IncidentResponse
        from app.schemas.knowledge import KnowledgeDocumentResponse

        project = await self.get_project_by_id(db, project_id)
        services = await service_repository.get_all_by_project(db, project.id)
        incidents = await incident_repository.get_all_by_project(db, project.id)
        knowledge = await knowledge_repository.get_all_by_project(db, project.id)

        return {
            "project": ProjectResponse.model_validate(project).model_dump(mode="json"),
            "services": [ServiceResponse.model_validate(s).model_dump(mode="json") for s in services],
            "incidents": [IncidentResponse.model_validate(i).model_dump(mode="json") for i in incidents],
            "knowledge": [KnowledgeDocumentResponse.model_validate(k).model_dump(mode="json") for k in knowledge],
            "investigations": [],
            "deployments": [],
            "logs": [],
            "exportedAt": datetime.now(timezone.utc).isoformat(),
        }


project_service = ProjectService()
