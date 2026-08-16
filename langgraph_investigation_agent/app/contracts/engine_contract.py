from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EngineEvidenceItem(BaseModel):
    """Input evidence item provided to the LangGraph engine."""
    evidence_id: str = Field(..., description="Unique evidence ID (e.g., EVD-LOG-1, EVD-DOC-1)")
    source_type: str = Field(..., description="Classification: 'log', 'document', 'image', 'telemetry', 'description'")
    source_name: str = Field(..., description="File name or descriptive title")
    content: str = Field(..., description="Raw text, parsed log lines, or document summary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata parameters")


class EngineIncidentInput(BaseModel):
    """Engine-owned standalone input contract."""
    incident_id: str = Field(..., description="Incident identifier")
    project_id: str = Field(default="default-project", description="Workspace project ID")
    title: str = Field(..., description="Incident headline title")
    description: str = Field(..., description="Detailed incident description")
    affected_service: str = Field(..., description="Primary affected microservice or component")
    timeline: Optional[str] = Field(default="Ongoing", description="Incident occurrence timeline")
    evidence: List[EngineEvidenceItem] = Field(default_factory=list, description="Attached evidence items")


class PrimaryRootCause(BaseModel):
    """Structured primary root cause in output contract."""
    title: str = Field(..., description="Clear title of suspected root cause")
    explanation: str = Field(..., description="Detailed technical explanation grounded in evidence")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Traceable confidence score (0-100%)")
    confidence_explanation: Optional[str] = Field(default=None, description="Explanation of confidence calculation")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of evidence directly supporting this root cause")
    contradicting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of evidence contradicting this root cause")
    affected_services: List[str] = Field(default_factory=list, description="Microservices impacted")
    verification: List[str] = Field(default_factory=list, description="Actionable verification checks to confirm/refute")


class AlternativeHypothesis(BaseModel):
    """Structured alternative hypothesis in output contract."""
    title: str = Field(..., description="Title of alternative root cause candidate")
    explanation: str = Field(..., description="Technical explanation")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confidence score (0-100%)")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of supporting evidence")
    contradicting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of contradicting evidence")


class RecommendedAction(BaseModel):
    """Actionable recommendation item."""
    category: str = Field(..., description="Immediate, Investigation, or Long-term")
    action: str = Field(..., description="Specific recommended action statement")
    reason: str = Field(..., description="Rationale backed by evidence")


class AnalysisMetadata(BaseModel):
    """Execution telemetry and health metadata."""
    confidence_source: str = Field(default="llm", description="'llm' or 'fallback'")
    nodes_executed: int = Field(default=0, description="Total LangGraph nodes executed")
    execution_time_seconds: float = Field(default=0.0, description="Execution duration in seconds")
    failed_llm_nodes: List[str] = Field(default_factory=list, description="Nodes that encountered LLM errors")


class EngineInvestigationOutput(BaseModel):
    """Engine-owned standalone output contract."""
    incident_id: str = Field(..., description="Incident identifier")
    status: str = Field(default="completed", description="Execution status: 'completed', 'degraded', 'failed'")
    analysis_complete: bool = Field(default=True, description="True if LLM analysis completed successfully")
    failure_reason: Optional[str] = Field(default=None, description="Failure details if status is degraded or failed")
    executive_summary: str = Field(..., description="High-level executive summary of RCA findings")
    primary_root_cause: PrimaryRootCause = Field(..., description="Definitive primary root cause")
    alternative_hypotheses: List[AlternativeHypothesis] = Field(default_factory=list, description="Ranked alternative candidates")
    timeline: List[str] = Field(default_factory=list, description="Timeline of observed events")
    evidence_chain: List[str] = Field(default_factory=list, description="Summary chain of accepted evidence items")
    recommended_actions: List[RecommendedAction] = Field(default_factory=list, description="Actionable recommendations")
    uncertainties: List[str] = Field(default_factory=list, description="Known information gaps or uncertainties")
    analysis_metadata: AnalysisMetadata = Field(default_factory=AnalysisMetadata, description="Engine execution metadata")
