from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.schemas.deployment import DeploymentCreate, DeploymentResponse
from app.services.deployment_service import deployment_service

router = APIRouter()


@router.get(
    "/projects/{project_id}/deployments",
    response_model=List[DeploymentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Project Change Timeline Deployments",
    description="Retrieves all deployment events across microservices in a project workspace ordered by deployedAt desc.",
)
async def get_deployments_by_project(
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[DeploymentResponse]:
    """Retrieves deployment change timeline for project_id."""
    deployments_orm = await deployment_service.get_deployments_by_project(db, project_id)
    return [DeploymentResponse.model_validate(d) for d in deployments_orm]


@router.get(
    "/services/{service_id}/deployments",
    response_model=List[DeploymentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Service Deployment History",
    description="Retrieves deployment history records for a specific microservice from PostgreSQL ordered by deployedAt desc.",
)
async def get_deployments_by_service(
    service_id: str = Path(..., description="Target service UUID or service name identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[DeploymentResponse]:
    """Retrieves deployment history for service_id."""
    deployments_orm = await deployment_service.get_deployments_by_service(db, service_id)
    return [DeploymentResponse.model_validate(d) for d in deployments_orm]


@router.post(
    "/services/{service_id}/deployments",
    response_model=DeploymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record Service Deployment Event",
    description="Registers a new deployment event in PostgreSQL for a target microservice.",
)
async def create_deployment(
    deployment_in: DeploymentCreate,
    service_id: str = Path(..., description="Target service UUID or service name identifier"),
    db: AsyncSession = Depends(get_db),
) -> DeploymentResponse:
    """Creates a new deployment record in PostgreSQL for service_id."""
    deployment_orm = await deployment_service.create_deployment(db, service_id, deployment_in)
    return DeploymentResponse.model_validate(deployment_orm)
