import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import ProjectModel
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Database access repository for Project operations."""

    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> List[ProjectModel]:
        """Fetch all workspace projects from PostgreSQL with optional search and environment filtering."""
        query = select(ProjectModel).order_by(ProjectModel.name.asc())

        if environment:
            query = query.where(ProjectModel.environment == environment)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    ProjectModel.name.ilike(search_pattern),
                    ProjectModel.slug.ilike(search_pattern),
                    ProjectModel.description.ilike(search_pattern),
                )
            )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, project_id: str) -> Optional[ProjectModel]:
        """Fetch a single project by primary key ID."""
        result = await db.execute(select(ProjectModel).where(ProjectModel.id == project_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[ProjectModel]:
        """Fetch a single project by unique slug."""
        result = await db.execute(select(ProjectModel).where(ProjectModel.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_id_or_slug(self, db: AsyncSession, identifier: str) -> Optional[ProjectModel]:
        """Fetch a single project matching either primary key ID or slug."""
        result = await db.execute(
            select(ProjectModel).where(
                or_(ProjectModel.id == identifier, ProjectModel.slug == identifier)
            )
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: ProjectCreate, slug: str) -> ProjectModel:
        """Create and persist a new ProjectModel record in PostgreSQL."""
        project_id = str(uuid.uuid4())
        db_obj = ProjectModel(
            id=project_id,
            name=obj_in.name,
            slug=slug,
            description=obj_in.description,
            environment=obj_in.environment.value if hasattr(obj_in.environment, "value") else str(obj_in.environment),
            owner_team=obj_in.owner_team,
            repository_url=obj_in.repository_url,
            service_count=0,
            active_incident_count=0,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ProjectModel,
        obj_in: ProjectUpdate,
    ) -> ProjectModel:
        """Partially update an existing ProjectModel record in PostgreSQL."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                if field == "environment" and hasattr(value, "value"):
                    setattr(db_obj, field, value.value)
                else:
                    setattr(db_obj, field, value)

        db_obj.updated_at = datetime.now(timezone.utc)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ProjectModel) -> None:
        """Delete a ProjectModel record from PostgreSQL using SQL delete statement so CASCADE foreign keys handle child tables."""
        await db.execute(delete(ProjectModel).where(ProjectModel.id == db_obj.id))
        await db.flush()


project_repository = ProjectRepository()
