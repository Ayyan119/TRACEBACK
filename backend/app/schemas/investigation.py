from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InvestigationRunResponse(BaseModel):
    """Pydantic schema for Investigation Run records returned by TRACEBACK API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    project_id: str
    investigation_number: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    incident_description: Optional[str] = None
    final_summary: Optional[str] = None
    root_cause: Optional[str] = None
    confidence: Optional[float] = None
    final_report: Optional[Dict[str, Any]] = Field(default=None, alias="final_report_json")
    selected_hypothesis: Optional[Dict[str, Any]] = Field(default=None, alias="selected_hypothesis_json")
    hypotheses: Optional[List[Dict[str, Any]]] = Field(default=None, alias="hypotheses_json")
    accepted_evidence: Optional[List[Dict[str, Any]]] = Field(default=None, alias="accepted_evidence_json")
    rejected_evidence: Optional[List[Dict[str, Any]]] = Field(default=None, alias="rejected_evidence_json")
    execution_trace: Optional[List[Dict[str, Any]]] = Field(default=None, alias="execution_trace_json")
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
