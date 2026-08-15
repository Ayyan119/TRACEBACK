from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ImageAnalysis(BaseModel):
    """Structured output for vision model image relevance & technical analysis."""
    relevant: bool = Field(description="True if the image is relevant to a production incident/error.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    observations: List[str] = Field(default_factory=list, description="Visual observations from the screenshot/diagram.")
    error_indicators: List[str] = Field(default_factory=list, description="Specific error status codes or stack traces visible.")
    technical_entities: List[str] = Field(default_factory=list, description="Services, URLs, or components identified.")
    reasoning_summary: str = Field(description="Summary of why the image is or is not relevant evidence.")


class DocumentAnalysis(BaseModel):
    """Structured output for incident document relevance & key point extraction."""
    relevant: bool = Field(description="True if the document is relevant to the reported incident.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    summary: str = Field(description="Executive summary of the document content.")
    key_points: List[str] = Field(default_factory=list, description="Key technical observations.")
    technical_entities: List[str] = Field(default_factory=list, description="Systems, APIs, databases, or services mentioned.")
    error_signatures: List[str] = Field(default_factory=list, description="Exceptions or error signatures found.")
    timestamps: List[str] = Field(default_factory=list, description="Relevant event timestamps extracted.")
    affected_services: List[str] = Field(default_factory=list, description="Services identified as degraded/impacted.")
    root_cause_hints: List[str] = Field(default_factory=list, description="Hints pointing to potential root causes.")


class LogQueryInput(BaseModel):
    """Structured parameters for log query tool execution."""
    incident_id: Optional[str] = None
    project_id: Optional[str] = None
    service: Optional[str] = Field(default=None, description="Target microservice name (e.g., checkout-service).")
    level: Optional[str] = Field(default=None, description="Log severity (e.g., ERROR, WARN, FATAL).")
    keyword: Optional[str] = Field(default=None, description="Substring keyword or error signature to search.")
    error_type: Optional[str] = Field(default=None, description="Exception class (e.g., ConnectionPoolTimeout).")
    date_from: Optional[str] = Field(default=None, description="ISO start date string (YYYY-MM-DD).")
    date_to: Optional[str] = Field(default=None, description="ISO end date string (YYYY-MM-DD).")
    limit: int = Field(default=50, ge=1, le=200, description="Max matching log records to return.")


class IncidentAnalysisDecision(BaseModel):
    """Self-RAG style decision on whether external knowledge base retrieval is required."""
    retrieval_required: bool = Field(description="True if Qdrant knowledge-base search is needed.")
    retrieval_reason: str = Field(description="Explanation of why retrieval is or is not required.")
    search_queries: List[str] = Field(default_factory=list, description="Semantic search queries if retrieval is required.")
    relevant_services: List[str] = Field(default_factory=list, description="Target services to query.")
    technical_topics: List[str] = Field(default_factory=list, description="Technical subjects (e.g. redis deadlock, P95 latency).")
    previous_incident_search_required: bool = Field(description="True if searching past resolved incident JSON points is needed.")


class RerankedItem(BaseModel):
    """Individual item evaluation during reranking node execution."""
    source_id: str = Field(description="ID of the retrieved knowledge chunk or previous incident.")
    source_type: str = Field(description="Type: knowledge_document or incident_history.")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance score to current investigation.")
    relevance_reason: str = Field(description="Rationale for keeping or discarding.")
    keep: bool = Field(description="True to retain for evidence synthesis, False to filter out.")


class EvidenceAnalysis(BaseModel):
    """Synthesized analysis combining all evidence, logs, and knowledge docs."""
    what_happened: str = Field(description="Concise description of the observed anomaly or outage.")
    when_it_happened: str = Field(description="Estimated start time and duration.")
    affected_service: str = Field(description="Primary impacted microservice or component.")
    symptoms: List[str] = Field(default_factory=list, description="Observed technical symptoms.")
    error_patterns: List[str] = Field(default_factory=list, description="Correlated error logs or stack traces.")
    correlations: List[str] = Field(default_factory=list, description="Cross-system or cross-service correlations.")
    possible_causes: List[str] = Field(default_factory=list, description="High-probability cause candidates.")
    contradictory_evidence: List[str] = Field(default_factory=list, description="Conflicting data points if any.")
    missing_information: List[str] = Field(default_factory=list, description="Unresolved information gaps.")


class Hypothesis(BaseModel):
    """Structured hypothesis for root-cause ranking."""
    hypothesis_id: str = Field(description="Unique hypothesis identifier (e.g. HYP-1).")
    title: str = Field(description="Clear title of suspected root cause.")
    description: str = Field(description="Detailed technical mechanism of failure.")
    confidence: float = Field(ge=0.0, le=100.0, description="Confidence percentage score (0-100%).")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of evidence supporting this hypothesis.")
    contradicting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of evidence contradicting this hypothesis.")
    affected_services: List[str] = Field(default_factory=list, description="Impacted microservices.")
    likely_root_cause: str = Field(description="Single primary root cause statement.")
    recommended_next_check: str = Field(description="Actionable verification or rollback recommendation.")


class HypothesisRanking(BaseModel):
    """Container for ranked list of hypotheses."""
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    primary_hypothesis_id: str = Field(description="ID of the highest confidence hypothesis.")


class HypothesisEvaluation(BaseModel):
    """Structured evaluation of evidence sufficiency and hypothesis validity."""
    evidence_sufficient: bool = Field(description="True if evidence is sufficient to confirm root cause without further investigation.")
    confidence: float = Field(ge=0.0, le=100.0, description="Evaluated confidence percentage (0-100%).")
    reason: str = Field(description="Explanation of why evidence is or is not sufficient.")
    missing_evidence: List[str] = Field(default_factory=list, description="Specific telemetry, logs, or evidence still needed if insufficient.")
    contradictions: List[str] = Field(default_factory=list, description="Unresolved conflicting observations.")
    recommended_next_action: str = Field(description="Next investigation action or final report generation.")
    selected_hypothesis_id: str = Field(description="ID of selected primary hypothesis.")


class FinalInvestigationReport(BaseModel):
    """Final comprehensive Root Cause Analysis (RCA) report structure."""
    incident_summary: str = Field(description="High-level executive summary of outage.")
    affected_services: List[str] = Field(default_factory=list, description="Degraded microservices.")
    timeline: str = Field(description="Incident start, detection, and investigation timeline.")
    observed_symptoms: List[str] = Field(default_factory=list, description="Technical symptoms.")
    accepted_evidence_summary: List[str] = Field(default_factory=list, description="Validated evidence sources.")
    retrieved_knowledge_summary: List[str] = Field(default_factory=list, description="Runbooks and technical docs referenced.")
    historical_incidents_summary: List[str] = Field(default_factory=list, description="Correlated past incidents.")
    root_cause: str = Field(description="Definitive primary root cause statement.")
    confidence: float = Field(ge=0.0, le=100.0, description="Final overall confidence score.")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence supporting final root cause.")
    contradictory_evidence: List[str] = Field(default_factory=list, description="Contradictions if any.")
    recommended_verification: str = Field(description="Immediate steps to verify fix.")
    recommended_remediation: str = Field(description="Long-term prevention recommendations.")
    investigation_limitations: List[str] = Field(default_factory=list, description="Known limitations or caveats.")
