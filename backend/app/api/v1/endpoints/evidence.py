from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.schemas.evidence import EvidenceCreate, EvidenceResponse
from app.services.evidence_service import evidence_service
from app.services.ingestion.file_extractor import IngestionError

router = APIRouter()


@router.get(
    "/incidents/{incident_id}/evidence",
    response_model=List[EvidenceResponse],
    status_code=status.HTTP_200_OK,
    summary="List Incident Evidence Items",
    description="Retrieves evidence items (logs, stack traces, screenshots, metrics) for an incident.",
)
async def get_incident_evidence(
    type_param: Optional[str] = Query(None, alias="type", description="Filter by evidence type (log, screenshot, metric, stack_trace, deployment, document)"),
    incident_id: str = Path(..., description="Target incident UUID or ticket code"),
    db: AsyncSession = Depends(get_db),
) -> List[EvidenceResponse]:
    """List all evidence items for incident_id."""
    items = await evidence_service.get_evidence_by_incident(db, incident_id, evidence_type=type_param)
    return [EvidenceResponse.model_validate(item) for item in items]


@router.post(
    "/incidents/{incident_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Evidence Item (JSON)",
    description="Adds a new evidence text snippet, log trace, or metric metadata item for an incident.",
)
async def create_evidence(
    evidence_in: EvidenceCreate,
    incident_id: str = Path(..., description="Target incident UUID or ticket code"),
    db: AsyncSession = Depends(get_db),
) -> EvidenceResponse:
    """Creates an evidence item for incident_id via JSON payload."""
    item = await evidence_service.create_evidence(db, incident_id, evidence_in)
    return EvidenceResponse.model_validate(item)


@router.post(
    "/incidents/{incident_id}/evidence/upload",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Binary Evidence File",
    description="Uploads a physical file (PDF, PNG, LOG, TXT) and attaches it as investigation evidence.",
)
async def upload_evidence_file(
    title: str = Form(..., description="Evidence title"),
    type_str: str = Form("log", alias="type", description="Evidence type (log, screenshot, document, stack_trace)"),
    source: str = Form("User Upload", description="Evidence origin source"),
    file: UploadFile = File(..., description="Binary or text file to upload"),
    incident_id: str = Path(..., description="Target incident UUID or ticket code"),
    db: AsyncSession = Depends(get_db),
) -> EvidenceResponse:
    """Uploads a binary file and creates an evidence record."""
    try:
        item = await evidence_service.upload_evidence_file(db, incident_id, type_str, title, source, file)
        return EvidenceResponse.model_validate(item)
    except IngestionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete(
    "/evidence/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Evidence Item",
    description="Deletes an evidence record from PostgreSQL.",
)
async def delete_evidence(
    evidence_id: str = Path(..., description="Evidence item UUID"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes an evidence item by ID."""
    await evidence_service.delete_evidence(db, evidence_id)
