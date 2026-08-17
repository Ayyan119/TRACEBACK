import operator
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Container for validated evidence items in the graph state."""
    evidence_id: str
    source_type: str  # image, document, log, description, knowledge, previous_incident
    source_name: str
    source_reference: Optional[str] = None
    content: str
    relevance: bool = True
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


def add_lists(left: List[Any], right: List[Any]) -> List[Any]:
    """Custom list reducer to combine list updates from parallel nodes cleanly."""
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right


class InvestigationState(TypedDict, total=False):
    """Strongly-typed LangGraph state representation for TRACEBACK AI Investigation Agent."""
    # Context Identifiers
    investigation_id: str
    incident_id: str
    project_id: str
    
    # Raw Incident Inputs
    incident_description: str
    incident_log_reference: Optional[Dict[str, Any]]
    services: List[str]
    service_metadata: Dict[str, Any]
    incident_documents: List[Dict[str, Any]]
    incident_images: List[Dict[str, Any]]
    
    # Processed Candidate Evidence (Annotated with reducer for parallel node updates)
    processed_document_evidence: Annotated[List[Dict[str, Any]], add_lists]
    processed_image_evidence: Annotated[List[Dict[str, Any]], add_lists]
    accepted_evidence: List[Dict[str, Any]]
    rejected_evidence: List[Dict[str, Any]]
    
    # Tool Execution Loop (max 5 tool iterations per cycle)
    log_query_history: List[Dict[str, Any]]
    retrieved_logs: List[Dict[str, Any]]
    tool_iterations: int
    tool_decision: Optional[str]
    
    # Main Investigation Loop (max 3 investigation cycles)
    investigation_iterations: int
    
    # Self-RAG Retrieval Phase
    retrieval_required: bool
    retrieval_reason: Optional[str]
    search_queries: List[str]
    previous_incident_search_required: bool
    retrieved_knowledge_documents: List[Dict[str, Any]]
    retrieved_previous_incidents: List[Dict[str, Any]]
    reranked_documents: List[Dict[str, Any]]
    

    # Analysis & Synthesis
    evidence_analysis: Optional[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    selected_hypothesis: Optional[Dict[str, Any]]
    confidence: float
    confidence_source: str  # "llm", "fallback", "unavailable"
    analysis_status: str    # "success", "degraded", "failed"
    investigation_summary: Optional[str]
    
    # Hypothesis Evaluation & Investigation Loop Controls
    hypothesis_evaluation: Optional[Dict[str, Any]]
    evidence_sufficient: bool
    grounding_validation: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
    
    # Observability & Safety (Annotated for parallel updates)
    failed_llm_nodes: Annotated[List[str], add_lists]
    errors: Annotated[List[str], add_lists]
    warnings: Annotated[List[str], add_lists]
    execution_trace: Annotated[List[Dict[str, Any]], add_lists]



