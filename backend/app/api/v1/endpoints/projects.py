from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import project_service

router = APIRouter()


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Workspace Projects",
    description="Retrieves a list of all workspace projects from PostgreSQL with optional search & environment filtering.",
)
async def get_projects(
    search: Optional[str] = Query(None, description="Search term for project name, slug, or description"),
    environment: Optional[str] = Query(None, description="Filter by environment tier (production, staging, development)"),
    db: AsyncSession = Depends(get_db),
) -> List[ProjectResponse]:
    """Retrieves all workspace projects from PostgreSQL."""
    projects_orm = await project_service.get_projects(db, search=search, environment=environment)
    return [ProjectResponse.model_validate(p) for p in projects_orm]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Project",
    description="Retrieves a single workspace project by ID or slug.",
)
async def get_project(
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Retrieves a single project from PostgreSQL by ID or slug."""
    project_orm = await project_service.get_project_by_id(db, project_id)
    return ProjectResponse.model_validate(project_orm)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workspace Project",
    description="Creates a new isolated workspace project in TRACEBACK.",
)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Creates a new workspace project record in PostgreSQL."""
    project_orm = await project_service.create_project(db, project_in)
    return ProjectResponse.model_validate(project_orm)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Workspace Project",
    description="Partially updates an existing workspace project attributes in PostgreSQL.",
)
async def update_project(
    project_in: ProjectUpdate,
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Partially updates a workspace project record in PostgreSQL."""
    project_orm = await project_service.update_project(db, project_id, project_in)
    return ProjectResponse.model_validate(project_orm)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Workspace Project",
    description="Permanently deletes a workspace project and all its isolated resources from PostgreSQL.",
)
async def delete_project(
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes a workspace project record from PostgreSQL."""
    await project_service.delete_project(db, project_id)


@router.get(
    "/{project_id}/export",
    status_code=status.HTTP_200_OK,
    summary="Export Workspace Project Data",
    description="Exports complete project configuration, services, incidents, and knowledge metadata.",
)
async def export_project(
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generates complete project export report."""
    return await project_service.export_project(db, project_id)
