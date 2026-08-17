from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.service import ServiceModel
from app.repositories.project_repository import project_repository
from app.repositories.service_repository import service_repository
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.project_service import project_service


class ServiceService:
    """Business logic service for Service operations."""

    async def get_services_by_project(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> List[ServiceModel]:
        """Retrieves all services scoped strictly to project_id with active incident health syncing."""
        project = await project_service.get_project_by_id(db, project_id)
        services = await service_repository.get_all_by_project(db, project.id)

        # Sync service health with active/identified incidents in PostgreSQL
        from app.repositories.incident_repository import incident_repository
        import json
        incidents = await incident_repository.get_all_by_project(db, project.id)
        
        def is_service_match(aff_raw: str, db_name: str) -> bool:
            aff = aff_raw.lower().replace("-", " ").replace("_", " ").strip()
            srv = db_name.lower().replace("-", " ").replace("_", " ").strip()
            return srv in aff or aff in srv or any(p in aff for p in srv.split() if len(p) > 3)

        affected_list = []
        for inc in incidents:
            if inc.status in ("Investigating", "Identified"):
                aff_list = list(inc.affected_services or [])
                if inc.affected_service:
                    aff_list.append(inc.affected_service)
                if inc.root_cause_summary:
                    try:
                        parsed = json.loads(inc.root_cause_summary)
                        report_aff = parsed.get("final_report", {}).get("affected_services", [])
                        if isinstance(report_aff, list):
                            aff_list.extend(report_aff)
                    except Exception:
                        pass
                
                for sname in aff_list:
                    if sname and isinstance(sname, str):
                        clean = sname.strip()
                        if clean.lower() not in ("backend", "core services", "backend services"):
                            affected_list.append((clean, inc))

        for srv in services:
            matching_inc = None
            for aff_raw, inc in affected_list:
                if is_service_match(aff_raw, srv.name):
                    matching_inc = inc
                    break

            if matching_inc:
                srv.health = "Critical" if matching_inc.severity in ("Critical", "High") else "Degraded"
                srv.error_rate_percent = 24.8 if matching_inc.severity in ("Critical", "High") else 15.4
                srv.recent_incidents_count = max(1, srv.recent_incidents_count or 1)
                db.add(srv)

        await db.commit()
        return services

    async def get_service_by_id(
        self,
        db: AsyncSession,
        service_id: str,
    ) -> ServiceModel:
        """Retrieves a single microservice by ID or name, or raises 404 ResourceNotFoundException."""
        service = await service_repository.get_by_id_or_name(db, service_id)
        if not service:
            raise ResourceNotFoundException("Service", service_id)
        return service

    async def create_service(
        self,
        db: AsyncSession,
        project_id: str,
        obj_in: ServiceCreate,
    ) -> ServiceModel:
        """Validates project existence and creates a new service scoped to project_id."""
        project = await project_service.get_project_by_id(db, project_id)

        existing = await service_repository.get_by_name_and_project(db, project.id, obj_in.name)
        if existing:
            raise BadRequestException(f"Service '{obj_in.name}' already exists in project '{project_id}'.")

        new_service = await service_repository.create(db, obj_in, project.id)

        project.service_count += 1
        db.add(project)
        await db.flush()

        return new_service

    async def update_service(
        self,
        db: AsyncSession,
        service_id: str,
        obj_in: ServiceUpdate,
    ) -> ServiceModel:
        """Updates microservice properties partially or raises 404."""
        service = await self.get_service_by_id(db, service_id)
        return await service_repository.update(db, service, obj_in)

    async def delete_service(
        self,
        db: AsyncSession,
        service_id: str,
    ) -> None:
        """Deletes a microservice and decrements the parent project's service_count."""
        service = await self.get_service_by_id(db, service_id)

        # Decrement parent project service_count if parent project exists
        project = await project_repository.get_by_id(db, service.project_id)
        if project and project.service_count > 0:
            project.service_count -= 1
            db.add(project)

        await service_repository.delete(db, service)


service_service = ServiceService()
