import json
import logging
import os
import time
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.deployment_repository import deployment_repository
from app.repositories.evidence_repository import evidence_repository
from app.repositories.incident_repository import incident_repository
from app.repositories.investigation_repository import investigation_repository
from app.repositories.knowledge_repository import knowledge_repository
from app.repositories.service_repository import service_repository
from app.schemas.incident import IncidentResponse, IncidentUpdate
from app.services.incident_service import incident_service
from app.services.incident_history_service import incident_history_service
from app.services.investigation.adapter import InvestigationAdapter
from app.services.investigation.schemas import (
    InvestigationInput,
    IncidentLogInput,
    IncidentDocumentInput,
    IncidentImageInput,
)

logger = logging.getLogger("traceback.services.ai_investigation")


def sanitize_error(message: str) -> str:
    """Sanitizes sensitive credentials, passwords, or connection strings from error messages."""
    import re
    cleaned = re.sub(r"://[^:]+:[^@]+@", "://***:***@", message)
    cleaned = re.sub(r"api[_-]?key[=\s:]+[^\s&]+", "api_key=***", cleaned, flags=re.IGNORECASE)
    return cleaned


class AIInvestigationService:
    """LangGraph / Autonomous AI Root-Cause Investigation Engine for TRACEBACK."""

    async def run_investigation(
        self,
        db: AsyncSession,
        incident_id: str,
        user_name: Optional[str] = None,
        user_role: Optional[str] = None,
        force_restart: bool = True,
    ) -> IncidentResponse:
        """Executes AI root-cause investigation workflow with full persistence and Qdrant history indexing."""
        target_user_name = user_name or "Ayyan Shahid"
        target_user_role = user_role or "Senior Software Engineer"

        # Dynamically set LangSmith project tracing name to the user's name
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = target_user_name
        logger.info(f"Set LangSmith project tracing name to user '{target_user_name}' ({target_user_role})")

        logger.info(f"AIInvestigationService.run_investigation starting for incident '{incident_id}' (User: {target_user_name}, ForceRestart: {force_restart})")

        # 1. Fetch target incident
        incident = await incident_service.get_incident_by_id(db, incident_id)

        # 2. Reset cached root cause summary if force_restart is requested
        if force_restart or not incident.root_cause_summary:
            incident.root_cause_summary = None
            incident.confidence = 0.0
            incident.status = "Investigating"
            db.add(incident)
            await db.commit()
            await db.refresh(incident)

        # 3. Create Investigation Run record (status = CREATED)
        inv_record = await investigation_repository.create(
            db=db,
            incident_id=incident.id,
            project_id=incident.project_id,
            incident_description=incident.description,
        )

        # 4. Transition status = RUNNING
        await investigation_repository.mark_running(db, inv_record.id)
        start_time = time.time()

        try:
            # 4. Gather attached evidence items
            evidence_items = await evidence_repository.get_all_by_incident(db, incident.id)

            log_items = [e for e in evidence_items if e.type == "log"]
            doc_items = [e for e in evidence_items if e.type in ("document", "file")]
            img_items = [e for e in evidence_items if e.type == "image"]

            if log_items:
                log_ref = IncidentLogInput(
                    file_name=log_items[0].title or f"{incident.code.lower()}_telemetry.log",
                    file_size_bytes=log_items[0].file_size or 1048576,
                    log_type="telemetry",
                )
            else:
                log_ref = IncidentLogInput(
                    file_name=f"{incident.code.lower()}_telemetry.log",
                    file_size_bytes=1048576,
                    log_type="telemetry",
                )

            doc_inputs = [
                IncidentDocumentInput(
                    name=d.title or "diagnostic_document.pdf",
                    content=d.raw_content or f"Incident document '{d.title}': {d.file_url or 'attachment content'}",
                )
                for d in doc_items
            ]

            img_inputs = [
                IncidentImageInput(
                    title=i.title or "Telemetry Screenshot",
                    file_url=i.file_url,
                    file_path=getattr(i, "file_path", None),
                )
                for i in img_items
            ]

            services = incident.affected_services or ([incident.affected_service] if incident.affected_service else ["checkout-service"])

            input_data = InvestigationInput(
                investigation_id=inv_record.id,
                incident_id=incident.id,
                project_id=incident.project_id,
                incident_description=incident.description,
                services=services,
                service_metadata={
                    s: {"environment": incident.environment or "production"} for s in services
                },
                incident_log_reference=log_ref,
                incident_documents=doc_inputs,
                incident_images=img_inputs,
            )

            # 5. Execute InvestigationAdapter -> LangGraph Agent Engine
            adapter = InvestigationAdapter()
            result = await adapter.arun(input_data)

            duration_ms = (time.time() - start_time) * 1000.0
            result_dict = result.model_dump()
            result_dict["investigation_run_id"] = inv_record.id
            result_dict["investigation_number"] = inv_record.investigation_number

            # 6. Complete Investigation Record in PostgreSQL (status = COMPLETED)
            await investigation_repository.mark_completed(
                db=db,
                investigation_id=inv_record.id,
                result_data=result_dict,
                duration_ms=duration_ms,
            )

            # 7. Update Incident Record
            json_payload = json.dumps(result_dict)
            update_dto = IncidentUpdate(
                status="Identified",
                root_cause_summary=json_payload,
                confidence=result.confidence,
            )
            updated_orm = await incident_repository.update(db, incident, update_dto)

            # 7b. Update Affected Services Health & Error Rate in PostgreSQL
            target_services = result_dict.get("final_report", {}).get("affected_services", [])
            if not target_services and incident.affected_services:
                target_services = incident.affected_services
            if not target_services and incident.affected_service:
                target_services = [incident.affected_service]

            all_db_services = await service_repository.get_all_by_project(db, incident.project_id)

            def is_service_match(aff_raw: str, db_name: str) -> bool:
                aff = aff_raw.lower().replace("-", " ").replace("_", " ").strip()
                srv = db_name.lower().replace("-", " ").replace("_", " ").strip()
                return srv in aff or aff in srv or any(p in aff for p in srv.split() if len(p) > 3)

            for s_name in target_services:
                if not s_name or not isinstance(s_name, str):
                    continue
                clean_name = s_name.strip()
                if clean_name.lower() in ("backend", "core services", "backend services"):
                    continue

                matched_srv = None
                for srv in all_db_services:
                    if is_service_match(clean_name, srv.name):
                        matched_srv = srv
                        break

                if matched_srv:
                    matched_srv.health = "Critical" if incident.severity in ("Critical", "High") else "Degraded"
                    matched_srv.error_rate_percent = 24.8 if incident.severity in ("Critical", "High") else 15.4
                    matched_srv.recent_incidents_count = max(1, (matched_srv.recent_incidents_count or 0) + 1)
                    db.add(matched_srv)
                    logger.info(f"Updated affected service '{matched_srv.name}' health to '{matched_srv.health}' (Error rate: {matched_srv.error_rate_percent}%)")
                else:
                    from app.schemas.service import ServiceCreate
                    new_srv_dto = ServiceCreate(
                        name=clean_name,
                        type="Backend",
                        description=f"Auto-discovered service impacted by incident {incident.code}",
                        environment=incident.environment or "Production",
                    )
                    new_srv = await service_repository.create(db, new_srv_dto, incident.project_id)
                    new_srv.health = "Critical" if incident.severity in ("Critical", "High") else "Degraded"
                    new_srv.error_rate_percent = 24.8 if incident.severity in ("Critical", "High") else 15.4
                    new_srv.recent_incidents_count = 1
                    db.add(new_srv)
                    logger.info(f"Auto-created affected service '{new_srv.name}' with health '{new_srv.health}'")

            await db.commit()

            # 8. STAGE 14 CRITICAL: Index completed incident into Qdrant as ONE atomic vector
            try:
                await incident_history_service.index_incident_history(db, updated_orm)
                logger.info(f"Successfully indexed incident '{incident.code}' into Qdrant history.")
            except Exception as hist_err:
                logger.warning(f"Failed to index incident history to Qdrant (continuing): {hist_err}")

            logger.info(
                f"AIInvestigationService completed run #{inv_record.investigation_number} "
                f"for incident '{incident.code}' in {duration_ms:.1f}ms (Confidence: {result.confidence}%)"
            )
            return IncidentResponse.model_validate(updated_orm)

        except Exception as e:
            sanitized = sanitize_error(str(e))
            logger.error(f"Investigation run #{inv_record.investigation_number} failed for incident '{incident.code}': {sanitized}")
            await investigation_repository.mark_failed(db, inv_record.id, sanitized)
            raise


ai_investigation_service = AIInvestigationService()
