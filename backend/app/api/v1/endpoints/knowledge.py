from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.schemas.knowledge import KnowledgeDocumentCreate, KnowledgeDocumentResponse
from app.services.knowledge_service import knowledge_service

router = APIRouter()


@router.get(
    "/projects/{project_id}/knowledge",
    response_model=List[KnowledgeDocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Workspace Knowledge Base Documents",
    description="Retrieves knowledge base documents (Architecture docs, Runbooks, Postmortems, API Specs) for a project workspace.",
)
async def get_project_knowledge_documents(
    category: Optional[str] = Query(None, description="Filter by category (Architecture, Runbook, API Spec, Postmortem, Incident Log)"),
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> List[KnowledgeDocumentResponse]:
    """List knowledge base documents for project_id."""
    docs = await knowledge_service.get_documents_by_project(db, project_id, category=category)
    return [KnowledgeDocumentResponse.model_validate(doc) for doc in docs]


@router.post(
    "/projects/{project_id}/knowledge",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Knowledge Document (JSON)",
    description="Adds a markdown or text knowledge document snippet to the workspace knowledge base.",
)
async def create_knowledge_document(
    document_in: KnowledgeDocumentCreate,
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeDocumentResponse:
    """Creates a knowledge document for project_id via JSON payload."""
    doc = await knowledge_service.create_document(db, project_id, document_in)
    return KnowledgeDocumentResponse.model_validate(doc)


@router.post(
    "/projects/{project_id}/knowledge/upload",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Knowledge Document File",
    description="Uploads a physical document (PDF, DOCX, TXT, MD, CSV, JSON) and indexes it into the project knowledge base.",
)
async def upload_knowledge_document_file(
    title: Optional[str] = Form(None, description="Document title"),
    category: str = Form("Architecture", description="Document category (Architecture, Runbook, Postmortem, API Spec)"),
    file: UploadFile = File(..., description="Document file to upload"),
    project_id: str = Path(..., description="Target project UUID or unique slug identifier"),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeDocumentResponse:
    """Uploads a document file and indexes it."""
    doc_title = title if title else (file.filename or "Untitled Document")
    doc = await knowledge_service.upload_document_file(db, project_id, category, doc_title, file)
    return KnowledgeDocumentResponse.model_validate(doc)


@router.delete(
    "/knowledge/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Knowledge Document",
    description="Deletes a document from the workspace knowledge base.",
)
async def delete_knowledge_document(
    document_id: str = Path(..., description="Knowledge document item UUID"),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes a knowledge document by ID."""
    await knowledge_service.delete_document(db, document_id)
