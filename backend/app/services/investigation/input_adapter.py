import logging
from typing import Dict, Any
from app.services.investigation.schemas import InvestigationInput
from app.services.investigation.exceptions import MissingLogReferenceError, InvalidInputError

logger = logging.getLogger("traceback.services.investigation.input_adapter")


class InputAdapter:
    """Translates TRACEBACK API/backend InvestigationInput into LangGraph InvestigationState."""

    @staticmethod
    def to_investigation_state(input_data: InvestigationInput) -> Dict[str, Any]:
        """Converts InvestigationInput schema into InvestigationState dictionary."""
        if not input_data:
            raise InvalidInputError("InvestigationInput cannot be null.")

        if not input_data.incident_id:
            raise InvalidInputError("incident_id is required.")

        if not input_data.project_id:
            raise InvalidInputError("project_id is required.")

        if not input_data.incident_log_reference or not input_data.incident_log_reference.file_name:
            raise MissingLogReferenceError(
                "Mandatory incident log reference is missing. Exactly one incident log file is required."
            )

        # Convert incident log reference to dict
        log_ref = input_data.incident_log_reference.model_dump()

        # Convert documents to raw dict list for process_documents node
        doc_list = [d.model_dump() for d in input_data.incident_documents] if input_data.incident_documents else []

        # Convert images to raw dict list for process_images node
        img_list = [i.model_dump() for i in input_data.incident_images] if input_data.incident_images else []

        # Ensure primary microservice is in services list
        services = list(input_data.services) if input_data.services else ["default-service"]

        investigation_state: Dict[str, Any] = {
            "incident_id": input_data.incident_id,
            "project_id": input_data.project_id,
            "incident_description": input_data.incident_description,
            "incident_log_reference": log_ref,
            "services": services,
            "service_metadata": input_data.service_metadata or {},
            "incident_documents": doc_list,
            "incident_images": img_list,
            # Initial state tracking parameters
            "processed_document_evidence": [],
            "processed_image_evidence": [],
            "accepted_evidence": [],
            "rejected_evidence": [],
            "log_query_history": [],
            "retrieved_logs": [],
            "tool_iterations": 0,
            "investigation_iterations": 0,
            "retrieved_knowledge_documents": [],
            "retrieved_previous_incidents": [],
            "reranked_documents": [],
            "hypotheses": [],
            "errors": [],
            "warnings": [],
            "execution_trace": [],
        }

        logger.info(
            f"InputAdapter: Successfully converted API payload for incident '{input_data.incident_id}' "
            f"({len(doc_list)} docs, {len(img_list)} images, log: {log_ref.get('file_name')})"
        )
        return investigation_state
