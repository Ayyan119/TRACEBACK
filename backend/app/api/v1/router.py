from fastapi import APIRouter
from app.api.v1.endpoints import deployments, evidence, health, incidents, knowledge, projects, services

api_v1_router = APIRouter()

# Health Endpoints
api_v1_router.include_router(health.router, tags=["Health"])

# Projects Endpoints
api_v1_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Services Endpoints
api_v1_router.include_router(services.router, tags=["Services"])

# Deployments Endpoints
api_v1_router.include_router(deployments.router, tags=["Deployments"])

# Incidents Endpoints
api_v1_router.include_router(incidents.router, tags=["Incidents"])

# Evidence Endpoints
api_v1_router.include_router(evidence.router, tags=["Evidence"])

# Knowledge Base Endpoints
api_v1_router.include_router(knowledge.router, tags=["Knowledge Base"])
