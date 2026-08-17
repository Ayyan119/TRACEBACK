from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.dependencies.user import get_current_user
from app.models.user import UserModel
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import project_service

router = APIRouter()


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List Workspace Projects",
    description="Retrieves workspace projects owned by the authenticated user from PostgreSQL.",
)
async def get_projects(
    search: Optional[str] = Query(None, description="Search term for project name, slug, or description"),
    environment: Optional[str] = Query(None, description="Filter by environment tier (production, staging, development)"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProjectResponse]:
    """Retrieves workspace projects belonging to current_user."""
    projects_orm = await project_service.get_projects(db, user_id=current_user.id, search=search, environment=environment)
    return [ProjectResponse.model_validate(p) for p in projects_orm]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Project",
    description="Retrieves a single workspace project by ID or slug owned by the authenticated user.",
)
async def get_project(
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Retrieves a single project from PostgreSQL by ID or slug owned by current_user."""
    project_orm = await project_service.get_project_by_id(db, project_id, user_id=current_user.id)
    return ProjectResponse.model_validate(project_orm)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workspace Project",
    description="Creates a new isolated workspace project in TRACEBACK owned by the authenticated user.",
)
async def create_project(
    project_in: ProjectCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Creates a new workspace project record in PostgreSQL owned by current_user."""
    project_orm = await project_service.create_project(db, project_in, user_id=current_user.id)
    return ProjectResponse.model_validate(project_orm)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Workspace Project",
    description="Partially updates an existing workspace project owned by the authenticated user.",
)
async def update_project(
    project_in: ProjectUpdate,
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Partially updates a workspace project record in PostgreSQL owned by current_user."""
    project_orm = await project_service.update_project(db, project_id, project_in, user_id=current_user.id)
    return ProjectResponse.model_validate(project_orm)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Workspace Project",
    description="Permanently deletes a workspace project owned by the authenticated user.",
)
async def delete_project(
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes a workspace project record from PostgreSQL owned by current_user."""
    await project_service.delete_project(db, project_id, user_id=current_user.id)


@router.get(
    "/{project_id}/export",
    status_code=status.HTTP_200_OK,
    summary="Export Workspace Project Data",
    description="Exports complete project configuration, services, incidents, and knowledge metadata.",
)
async def export_project(
    project_id: str = Path(..., description="Project UUID or unique slug identifier"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generates complete project export report owned by current_user."""
    return await project_service.export_project(db, project_id, user_id=current_user.id)
