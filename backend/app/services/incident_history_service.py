import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from qdrant_client.http import models as qmodels
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import IncidentModel
from app.models.incident_history import IncidentHistoryModel
from app.repositories.evidence_repository import evidence_repository
from app.repositories.incident_history_repository import incident_history_repository
from app.repositories.log_repository import log_repository
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class IncidentHistoryService:
    """Service layer orchestrating atomic Incident History serialization & Qdrant vector indexing."""

    async def build_historical_representation(
        self,
        db: AsyncSession,
        incident: IncidentModel,
    ) -> Dict[str, Any]:
        """Constructs a clean, deterministic JSON representation of a resolved incident."""
        evidence_items = await evidence_repository.get_all_by_incident(db, incident.id)
        evidence_summaries = []
        for ev in evidence_items:
            evidence_summaries.append({
                "id": ev.id,
                "type": ev.type,
                "title": ev.title,
                "summary": ev.raw_content[:500] if ev.raw_content else None,
            })

        log_records = await log_repository.get_all_by_incident(db, incident.id)

        payload = {
            "incident_id": incident.id,
            "incident_code": incident.code,
            "project_id": incident.project_id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
            "affected_service": incident.affected_service,
            "affected_services": incident.affected_services or [],
            "environment": incident.environment,
            "reporter": incident.reporter,
            "detected_at": incident.detected_at.isoformat() if incident.detected_at else None,
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else (
                datetime.now(timezone.utc).isoformat()
            ),
            "duration": incident.duration,
            "confidence": incident.confidence,
            "root_cause_summary": incident.root_cause_summary or "Investigation completed.",
            "evidence_count": len(evidence_items),
            "evidence_summaries": evidence_summaries,
            "log_records_count": len(log_records),
            "archived_at": datetime.now(timezone.utc).isoformat(),
        }
        return payload

    async def index_incident_history(
        self,
        db: AsyncSession,
        incident: IncidentModel,
    ) -> IncidentHistoryModel:
        """Indexes resolved incident as ONE atomic Qdrant point with source_type='incident_history'."""
        historical_payload = await self.build_historical_representation(db, incident)

        # Build clean textual representation for embedding vector computation
        text_lines = [
            f"Historical Incident: {incident.code} - {incident.title}",
            f"Project ID: {incident.project_id}",
            f"Severity: {incident.severity} | Status: {incident.status} | Environment: {incident.environment}",
            f"Affected Services: {incident.affected_service} ({', '.join(incident.affected_services or [])})",
            f"Description:\n{incident.description}",
        ]
        if incident.root_cause_summary:
            text_lines.append(f"Root Cause Summary:\n{incident.root_cause_summary}")
        if historical_payload.get("evidence_summaries"):
            text_lines.append("Evidence Summaries:")
            for ev_s in historical_payload["evidence_summaries"]:
                text_lines.append(f"- [{ev_s['type']}] {ev_s['title']}: {ev_s['summary'] or 'N/A'}")

        embedding_text = "\n".join(text_lines)

        # Generate single dense vector
        vector = embedding_service.embed_text(embedding_text)
        dim = embedding_service.embedding_dim
        vector_store.ensure_collection(dimension=dim)

        # Deterministic Qdrant Point ID derived from SHA256 of incident_id
        hash_digest = hashlib.sha256(f"incident_history:{incident.id}".encode("utf-8")).hexdigest()
        point_uuid = f"{hash_digest[:8]}-{hash_digest[8:12]}-{hash_digest[12:16]}-{hash_digest[16:20]}-{hash_digest[20:32]}"

        # Upsert record in PostgreSQL
        history_record = await incident_history_repository.create_or_update(
            db=db,
            incident_id=incident.id,
            project_id=incident.project_id,
            incident_code=incident.code,
            historical_payload=historical_payload,
            qdrant_point_id=point_uuid,
            status="indexed",
        )

        qdrant_payload = {
            "project_id": incident.project_id,
            "source_type": "incident_history",
            "source_id": history_record.id,
            "incident_id": incident.id,
            "incident_code": incident.code,
            "title": incident.title,
            "severity": incident.severity,
            "affected_service": incident.affected_service,
            "text": embedding_text,
            "embedding_text": embedding_text,
            "historical_payload": historical_payload,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Idempotent cleanup of old history point for this incident ID
        vector_store.delete_source_vectors(source_type="incident_history", source_id=history_record.id)

        # Upsert single logical point into Qdrant
        point = qmodels.PointStruct(
            id=point_uuid,
            vector=vector,
            payload=qdrant_payload,
        )
        vector_store.upsert_chunks([point])

        logger.info(
            f"[INCIDENT-HISTORY] Successfully indexed incident '{incident.code}' (ID: {incident.id}) "
            f"as 1 atomic point into Qdrant (Point ID: {point_uuid})."
        )
        return history_record

    async def delete_incident_history(self, db: AsyncSession, incident_id: str) -> None:
        """Deletes incident history from PostgreSQL and Qdrant."""
        history = await incident_history_repository.get_by_incident_id(db, incident_id)
        if history:
            vector_store.delete_source_vectors(source_type="incident_history", source_id=history.id)
            await incident_history_repository.delete_by_incident_id(db, incident_id)


incident_history_service = IncidentHistoryService()
