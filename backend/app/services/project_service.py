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
        user_id: Optional[str] = None,
        search: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> List[ProjectModel]:
        """Retrieves list of workspace projects belonging to user_id with optional filters."""
        return await project_repository.get_all(db, user_id=user_id, search=search, environment=environment)

    async def get_project_by_id(
        self, db: AsyncSession, project_id: str, user_id: Optional[str] = None
    ) -> ProjectModel:
        """Retrieves a single project by ID or slug scoped to user_id, or raises 404 ResourceNotFoundException."""
        project = await project_repository.get_by_id_or_slug(db, project_id, user_id=user_id)
        if not project:
            raise ResourceNotFoundException("Project", project_id)
        return project

    async def create_project(
        self, db: AsyncSession, obj_in: ProjectCreate, user_id: str
    ) -> ProjectModel:
        """Validates business rules and creates a new project workspace owned by user_id."""
        slug = obj_in.slug if obj_in.slug else self.generate_slug(obj_in.name)

        existing = await project_repository.get_by_slug(db, slug)
        if existing:
            raise BadRequestException(f"Project with slug '{slug}' already exists.")

        return await project_repository.create(db, obj_in, slug, user_id=user_id)

    async def update_project(
        self,
        db: AsyncSession,
        project_id: str,
        obj_in: ProjectUpdate,
        user_id: Optional[str] = None,
    ) -> ProjectModel:
        """Updates project properties partially or raises 404."""
        project = await self.get_project_by_id(db, project_id, user_id=user_id)
        return await project_repository.update(db, project, obj_in)

    async def delete_project(
        self, db: AsyncSession, project_id: str, user_id: Optional[str] = None
    ) -> None:
        """Deletes a workspace project and its isolated resources or raises 404."""
        project = await self.get_project_by_id(db, project_id, user_id=user_id)
        await project_repository.delete(db, project)

    async def export_project(
        self, db: AsyncSession, project_id: str, user_id: Optional[str] = None
    ) -> dict:
        """Generates export data report dictionary for a project concurrently."""
        import asyncio
        from datetime import datetime, timezone
        from app.repositories.service_repository import service_repository
        from app.repositories.incident_repository import incident_repository
        from app.repositories.knowledge_repository import knowledge_repository
        from app.schemas.project import ProjectResponse
        from app.schemas.service import ServiceResponse
        from app.schemas.incident import IncidentResponse
        from app.schemas.knowledge import KnowledgeDocumentResponse

        project = await self.get_project_by_id(db, project_id, user_id=user_id)

        # Parallelize independent database read queries
        services, incidents, knowledge = await asyncio.gather(
            service_repository.get_all_by_project(db, project.id),
            incident_repository.get_all_by_project(db, project.id),
            knowledge_repository.get_all_by_project(db, project.id),
        )

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
