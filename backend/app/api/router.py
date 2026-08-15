from fastapi import APIRouter
from app.api.v1.router import api_v1_router
from app.core.config import settings

root_api_router = APIRouter()

# Register v1 router under /api/v1 prefix
root_api_router.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
