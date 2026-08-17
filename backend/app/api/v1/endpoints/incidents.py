from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Body, Depends, File, Form, Header, HTTPException, Path, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate
from app.schemas.incident_history import IncidentHistoryResponse
from app.schemas.investigation import InvestigationRunResponse
from app.schemas.log import LogRecordResponse
from app.services.ai_investigation_service import ai_investigation_service
from app.services.evidence_service import evidence_service
from app.services.incident_history_service import incident_history_service
from app.services.incident_service import incident_service
from app.services.log_service import log_service
from app.repositories.incident_history_repository import incident_history_repository
from app.repositories.investigation_repository import investigation_repository

router = APIRouter()


@router.get(
    "/projects/{project_id}/incidents",
    response_model=List[IncidentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Project Incidents",
    description="Retrieves incident reports belonging to a project workspace from PostgreSQL with optional severity & status filtering.",
)
async def get_incidents_by_project(
    severity: Optional[str] = Query(None, description="Filter by severity level (Critical, High, Medium, Low)"),
    status_param: Optional[str] = Query(None, alias="status", description="Filter by status (Investigating, Identified, Monitoring, Resolved)"),
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[IncidentResponse]:
    """Retrieves incidents from PostgreSQL for project_id."""
    incidents_orm = await incident_service.get_incidents_by_project(db, project_id, severity=severity, status=status_param)
    return [IncidentResponse.model_validate(inc) for inc in incidents_orm]


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Incident Details",
    description="Retrieves details for a single incident record by UUID or ticket code (e.g. INC-1001).",
)
async def get_incident(
    incident_id: str = Path(..., description="Incident UUID or ticket code identifier (e.g. INC-1001)"),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Retrieves a single incident from PostgreSQL by ID or code."""
    incident_orm = await incident_service.get_incident_by_id(db, incident_id)
    return IncidentResponse.model_validate(incident_orm)


@router.post(
    "/projects/{project_id}/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Incident Report (JSON)",
    description="Creates a new incident record in PostgreSQL scoped to a project workspace.",
)
async def create_incident(
    incident_in: IncidentCreate,
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Creates a new incident record in PostgreSQL for project_id."""
    incident_orm = await incident_service.create_incident(db, project_id, incident_in)
    return IncidentResponse.model_validate(incident_orm)


@router.post(
    "/projects/{project_id}/incidents/with-log",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Incident Report with Compulsory Log File",
    description="Creates a new incident record and processes the mandatory log file into structured log records.",
)
async def create_incident_with_log(
    title: str = Form(..., description="Incident title"),
    description: str = Form(..., description="Incident symptom description"),
    severity: str = Form("High", description="Severity level"),
    affected_service: str = Form("API Service", description="Affected service name"),
    environment: str = Form("Production", description="Target environment"),
    log_file: UploadFile = File(..., description="Compulsory log file"),
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Creates an incident requiring a mandatory log file."""
    if not log_file or not log_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A log file is required to create an incident.")

    incident_in = IncidentCreate(
        title=title,
        description=description,
        severity=severity,
        affected_service=affected_service,
        environment=environment,
    )
    incident_orm = await incident_service.create_incident(db, project_id, incident_in)

    # Ingest compulsory log file into PostgreSQL log_records table
    try:
        await evidence_service.upload_evidence_file(
            db=db,
            incident_id=incident_orm.id,
            type_str="log",
            title=f"Mandatory Log: {log_file.filename}",
            source="Incident Creation",
            file=log_file,
        )
    except Exception as e:
        logger_msg = str(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to process required log file: {logger_msg}")

    return IncidentResponse.model_validate(incident_orm)


@router.patch(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Incident Status or Root-Cause Summary",
    description="Partially updates incident attributes, status lifecycle (Resolved), or AI root-cause summary in PostgreSQL.",
)
async def update_incident(
    incident_in: IncidentUpdate,
    incident_id: str = Path(..., description="Incident UUID or ticket code identifier (e.g. INC-1001)"),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Partially updates an incident record in PostgreSQL."""
    incident_orm = await incident_service.update_incident(db, incident_id, incident_in)
    return IncidentResponse.model_validate(incident_orm)


class InvestigatePayload(BaseModel):
    force_restart: bool = True
    user_name: Optional[str] = None
    user_role: Optional[str] = None

@router.post(
    "/incidents/{incident_id}/investigate",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Run AI Root-Cause Investigation Agent",
    description="Triggers the LangGraph AI investigation workflow analyzing telemetry evidence, deployments, and RAG knowledge docs.",
)
async def run_ai_investigation(
    incident_id: str = Path(..., description="Incident UUID or ticket code identifier (e.g. INC-1001)"),
    payload: Optional[InvestigatePayload] = Body(None),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    """Triggers AI investigation workflow and returns updated incident."""
    name = (payload and payload.user_name) or x_user_name or "Ayyan Shahid"
    role = (payload and payload.user_role) or x_user_role or "Senior Software Engineer"
    force_restart = payload.force_restart if payload else True

    return await ai_investigation_service.run_investigation(
        db=db,
        incident_id=incident_id,
        user_name=name,
        user_role=role,
        force_restart=force_restart,
    )


@router.get(
    "/incidents/{incident_id}/investigations",
    response_model=List[InvestigationRunResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Investigation Runs for Incident",
    description="Retrieves persistent investigation runs for an incident ordered by investigation_number desc.",
)
async def get_incident_investigations(
    incident_id: str = Path(..., description="Incident UUID or code"),
    db: AsyncSession = Depends(get_db),
) -> List[InvestigationRunResponse]:
    """Retrieves all investigation runs for an incident."""
    runs = await investigation_repository.get_all_by_incident(db, incident_id)
    return [InvestigationRunResponse.model_validate(r) for r in runs]


@router.get(
    "/incidents/{incident_id}/investigations/{investigation_id}",
    response_model=InvestigationRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Investigation Run Detail",
    description="Retrieves a specific investigation run record with full evidence, report, and execution trace.",
)
async def get_investigation_run(
    investigation_id: str = Path(..., description="Investigation run UUID"),
    incident_id: str = Path(..., description="Incident UUID or code"),
    db: AsyncSession = Depends(get_db),
) -> InvestigationRunResponse:
    """Retrieves a single investigation run."""
    run = await investigation_repository.get_by_id(db, investigation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Investigation run '{investigation_id}' not found.")
    return InvestigationRunResponse.model_validate(run)


@router.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Incident Report",
    description="Deletes an incident record from PostgreSQL and decrements parent project's active_incident_count.",
)
async def delete_incident(
    incident_id: str = Path(..., description="Incident UUID or ticket code identifier (e.g. INC-1001)"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes an incident record from PostgreSQL."""
    await incident_service.delete_incident(db, incident_id)


@router.get(
    "/projects/{project_id}/incident-history",
    response_model=List[IncidentHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Project Incident History",
    description="Retrieves historical representations of resolved incidents for a project.",
)
async def get_project_incident_history(
    project_id: str = Path(..., description="Target project UUID or slug"),
    db: AsyncSession = Depends(get_db),
) -> List[IncidentHistoryResponse]:
    """Retrieves incident history records for project_id."""
    histories = await incident_history_repository.get_all_by_project(db, project_id)
    return [IncidentHistoryResponse.model_validate(h) for h in histories]


@router.post(
    "/incidents/{incident_id}/history/reindex",
    response_model=IncidentHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Re-index Incident History into Qdrant",
    description="Manually re-indexes a resolved incident into Qdrant as ONE atomic incident history point.",
)
async def reindex_incident_history(
    incident_id: str = Path(..., description="Incident UUID or code"),
    db: AsyncSession = Depends(get_db),
) -> IncidentHistoryResponse:
    """Re-indexes an incident into Qdrant history."""
    incident = await incident_service.get_incident_by_id(db, incident_id)
    history = await incident_history_service.index_incident_history(db, incident)
    return IncidentHistoryResponse.model_validate(history)


@router.get(
    "/projects/{project_id}/logs",
    response_model=List[LogRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Query Structured Project Logs",
    description="Queries structured PostgreSQL log records for a project with optional filters for incident, level, service, timestamp, and keyword.",
)
async def query_project_logs(
    project_id: str = Path(..., description="Target project UUID"),
    incident_id: Optional[str] = Query(None, description="Filter by incident ID"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    level: Optional[str] = Query(None, description="Filter by log level (ERROR, WARN, INFO)"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    keyword: Optional[str] = Query(None, description="Filter by message/raw text keyword"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
) -> List[LogRecordResponse]:
    """Queries structured log records from PostgreSQL."""
    logs = await log_service.query_logs(
        db=db,
        project_id=project_id,
        incident_id=incident_id,
        start_date=start_date,
        end_date=end_date,
        level=level,
        service=service,
        keyword=keyword,
        limit=limit,
        offset=offset,
    )
    return [LogRecordResponse.model_validate(l) for l in logs]
