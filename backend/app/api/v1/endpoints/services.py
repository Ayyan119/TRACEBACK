from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate
from app.services.service_service import service_service

router = APIRouter()


@router.get(
    "/projects/{project_id}/services",
    response_model=List[ServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="List Services in Project Workspace",
    description="Retrieves all microservices belonging to a project workspace from PostgreSQL.",
)
async def get_services_by_project(
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[ServiceResponse]:
    """Retrieves all microservices from PostgreSQL for a specific project_id."""
    services_orm = await service_service.get_services_by_project(db, project_id)
    return [ServiceResponse.model_validate(s) for s in services_orm]


@router.get(
    "/services/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Service Details",
    description="Retrieves details for a single microservice by UUID or service name.",
)
async def get_service(
    service_id: str = Path(..., description="Service UUID or service name identifier"),
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """Retrieves a single microservice from PostgreSQL by ID or name."""
    service_orm = await service_service.get_service_by_id(db, service_id)
    return ServiceResponse.model_validate(service_orm)


@router.post(
    "/projects/{project_id}/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Service in Project Workspace",
    description="Creates a new microservice in PostgreSQL scoped strictly to project_id.",
)
async def create_service(
    service_in: ServiceCreate,
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """Creates a new microservice record in PostgreSQL scoped to project_id."""
    service_orm = await service_service.create_service(db, project_id, service_in)
    return ServiceResponse.model_validate(service_orm)


@router.patch(
    "/services/{service_id}",
    response_model=ServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Service Details or Metrics",
    description="Partially updates microservice attributes or live operational metrics in PostgreSQL.",
)
async def update_service(
    service_in: ServiceUpdate,
    service_id: str = Path(..., description="Service UUID or service name identifier"),
    db: AsyncSession = Depends(get_db),
) -> ServiceResponse:
    """Partially updates a microservice record in PostgreSQL."""
    service_orm = await service_service.update_service(db, service_id, service_in)
    return ServiceResponse.model_validate(service_orm)


@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Microservice",
    description="Deletes a microservice record from PostgreSQL and decrements parent project's service_count.",
)
async def delete_service(
    service_id: str = Path(..., description="Service UUID or service name identifier"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes a microservice record from PostgreSQL."""
    await service_service.delete_service(db, service_id)
