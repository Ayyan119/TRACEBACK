from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceNotFoundException
from app.models.incident import IncidentModel
from app.repositories.incident_repository import incident_repository
from app.repositories.project_repository import project_repository
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.project_service import project_service


class IncidentService:
    """Business logic service for Incident operations."""

    async def get_incidents_by_project(
        self,
        db: AsyncSession,
        project_id: str,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[IncidentModel]:
        """Retrieves incidents scoped strictly to project_id with optional severity and status filters."""
        project = await project_service.get_project_by_id(db, project_id)
        return await incident_repository.get_all_by_project(db, project.id, severity=severity, status=status)

    async def get_incident_by_id(
        self,
        db: AsyncSession,
        incident_id: str,
    ) -> IncidentModel:
        """Retrieves a single incident record by ID or code, or raises 404 ResourceNotFoundException."""
        incident = await incident_repository.get_by_id_or_code(db, incident_id)
        if not incident:
            raise ResourceNotFoundException("Incident", incident_id)
        return incident

    async def create_incident(
        self,
        db: AsyncSession,
        project_id: str,
        obj_in: IncidentCreate,
    ) -> IncidentModel:
        """Validates project existence and creates a new incident record in PostgreSQL."""
        project = await project_service.get_project_by_id(db, project_id)

        code = await incident_repository.get_next_code(db)

        new_incident = await incident_repository.create(
            db=db,
            obj_in=obj_in,
            project_id=project.id,
            code=code,
        )

        project.active_incident_count += 1
        db.add(project)
        await db.flush()

        # Store newly created incident into Qdrant & PostgreSQL historical memory
        try:
            from app.services.incident_history_service import incident_history_service
            await incident_history_service.index_incident_history(db, new_incident)
            import logging
            logging.getLogger(__name__).info(f"Automatically stored new incident '{new_incident.code}' into historical vector memory.")
        except Exception as hist_err:
            import logging
            logging.getLogger(__name__).warning(f"Failed to index newly created incident '{new_incident.code}' into Qdrant history (continuing): {hist_err}")

        return new_incident

    async def update_incident(
        self,
        db: AsyncSession,
        incident_id: str,
        obj_in: IncidentUpdate,
    ) -> IncidentModel:
        """Updates incident properties partially, keeps active_incident_count in sync, and indexes resolved incident history into Qdrant."""
        from app.services.incident_history_service import incident_history_service

        incident = await self.get_incident_by_id(db, incident_id)
        old_status = incident.status

        updated_incident = await incident_repository.update(db, incident, obj_in)
        new_status = updated_incident.status

        if old_status != new_status:
            project = await project_repository.get_by_id(db, updated_incident.project_id)
            if project:
                if new_status == "Resolved" and old_status != "Resolved" and project.active_incident_count > 0:
                    project.active_incident_count -= 1
                    db.add(project)
                elif old_status == "Resolved" and new_status != "Resolved":
                    project.active_incident_count += 1
                    db.add(project)
                await db.flush()

        # If incident is Resolved, reset affected services back to Healthy and index into Qdrant
        if new_status == "Resolved":
            try:
                from app.repositories.service_repository import service_repository
                import json

                aff_list = list(updated_incident.affected_services or [])
                if updated_incident.affected_service:
                    aff_list.append(updated_incident.affected_service)
                if updated_incident.root_cause_summary:
                    try:
                        parsed = json.loads(updated_incident.root_cause_summary)
                        report_aff = parsed.get("final_report", {}).get("affected_services", [])
                        if isinstance(report_aff, list):
                            aff_list.extend(report_aff)
                    except Exception:
                        pass

                all_services = await service_repository.get_all_by_project(db, updated_incident.project_id)
                def is_service_match(aff_raw: str, db_name: str) -> bool:
                    aff = aff_raw.lower().replace("-", " ").replace("_", " ").strip()
                    srv = db_name.lower().replace("-", " ").replace("_", " ").strip()
                    return srv in aff or aff in srv or any(p in aff for p in srv.split() if len(p) > 3)

                for srv in all_services:
                    for aff_raw in aff_list:
                        if aff_raw and isinstance(aff_raw, str) and is_service_match(aff_raw, srv.name):
                            srv.health = "Healthy"
                            srv.error_rate_percent = 0.0
                            srv.recent_incidents_count = max(0, (srv.recent_incidents_count or 1) - 1)
                            db.add(srv)
                            break

                await db.flush()
                await incident_history_service.index_incident_history(db, updated_incident)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed during incident resolution updates for {updated_incident.id}: {e}")

        return updated_incident

    async def delete_incident(
        self,
        db: AsyncSession,
        incident_id: str,
    ) -> None:
        """Deletes an incident record, cleans up incident history & Qdrant points, and decrements parent project active_incident_count."""
        from app.services.incident_history_service import incident_history_service

        incident = await self.get_incident_by_id(db, incident_id)

        # Cleanup related Incident History and Qdrant points
        try:
            await incident_history_service.delete_incident_history(db, incident.id)
        except Exception:
            pass

        project = await project_repository.get_by_id(db, incident.project_id)
        if project and project.active_incident_count > 0:
            project.active_incident_count -= 1
            db.add(project)

        await incident_repository.delete(db, incident)


incident_service = IncidentService()
