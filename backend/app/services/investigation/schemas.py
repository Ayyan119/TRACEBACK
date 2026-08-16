from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class IncidentDocumentInput(BaseModel):
    """Uploaded incident document attachment for investigation."""
    name: str = Field(..., description="Document file name (e.g. diagnostic_report.pdf)")
    content: str = Field(..., description="Extracted text content of the document (max 3 pages)")


class IncidentImageInput(BaseModel):
    """Uploaded incident image/screenshot attachment for vision analysis."""
    title: str = Field(..., description="Screenshot title or descriptive label")
    file_url: Optional[str] = Field(None, description="Public/signed web URL to image file")
    file_path: Optional[str] = Field(None, description="Local filesystem path to image file")


class IncidentLogInput(BaseModel):
    """Mandatory incident log reference file."""
    file_name: str = Field(..., description="Parsed log file name in storage (e.g. app_telemetry.log)")
    file_size_bytes: int = Field(..., ge=0, description="Log file size in bytes")
    log_type: str = Field(default="telemetry", description="Log classification (telemetry, application, database)")


class InvestigationInput(BaseModel):
    """Clean API input payload passed into the Investigation Adapter."""
    incident_id: str = Field(..., description="Unique incident ticket UUID")
    project_id: str = Field(..., description="Parent workspace project UUID")
    incident_description: str = Field(..., description="Detailed problem statement or report (max 2,000 words)")
    services: List[str] = Field(default_factory=list, description="Target impacted microservices")
    service_metadata: Dict[str, Any] = Field(default_factory=dict, description="Environment and microservice metadata parameters")
    incident_log_reference: IncidentLogInput = Field(..., description="MANDATORY parsed log file reference")
    incident_documents: List[IncidentDocumentInput] = Field(default_factory=list, description="Optional incident documents (max 10 combined)")
    incident_images: List[IncidentImageInput] = Field(default_factory=list, description="Optional incident screenshots (max 10 combined)")

    @field_validator("incident_description")
    @classmethod
    def validate_description_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Incident description cannot be empty.")
        return v


class InvestigationResult(BaseModel):
    """Clean API output response returned from the Investigation Adapter."""
    investigation_id: str = Field(..., description="Graph execution run UUID")
    incident_id: str = Field(..., description="Target incident ticket UUID")
    status: str = Field(default="COMPLETED", description="Investigation status (COMPLETED, DEGRADED, FAILED)")
    confidence: float = Field(..., ge=0.0, le=100.0, description="AI root-cause confidence percentage (0-100%)")
    confidence_source: str = Field(default="llm", description="Source of confidence score: 'llm', 'fallback', 'unavailable'")
    analysis_status: str = Field(default="success", description="Status of LLM analysis: 'success', 'degraded', 'failed'")
    failed_llm_nodes: List[str] = Field(default_factory=list, description="LangGraph nodes that failed LLM invocation")
    investigation_summary: str = Field(..., description="Executive summary statement")
    final_report: Optional[Dict[str, Any]] = Field(None, description="Complete Root Cause Analysis (RCA) document")
    selected_hypothesis: Optional[Dict[str, Any]] = Field(None, description="Primary root-cause hypothesis")
    hypotheses: List[Dict[str, Any]] = Field(default_factory=list, description="Ranked candidate hypotheses")
    evidence_analysis: Optional[Dict[str, Any]] = Field(None, description="Synthesized evidence analysis and symptoms")
    accepted_evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Validated accepted evidence items")
    rejected_evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Discarded irrelevant files and reasons")
    log_query_history: List[Dict[str, Any]] = Field(default_factory=list, description="Log tool execution audit log")
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list, description="Graph node execution timeline")
