import os
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import root_api_router
from app.api.v1.endpoints import health
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler
from app.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})")
    try:
        from app.db.session import engine, AsyncSessionLocal
        from app.db.base import Base
        from app.services.user_service import user_service

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            await user_service.get_or_create_default_user(session)
            await session.commit()

        logger.info("Database tables and seed profiles initialized successfully.")
    except Exception as e:
        logger.error(f"Database startup initialization error: {e}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=f"{settings.APP_NAME} REST API",
    description="AI-powered production incident investigation and root cause analysis platform backend.",
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration (allows any localhost or 127.0.0.1 port in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)

# Top-level infrastructure health check endpoint (/health)
app.include_router(health.router, tags=["Health"])

# Register API Router (/api/v1)
app.include_router(root_api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
