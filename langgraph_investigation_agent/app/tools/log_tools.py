import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import config
from app.models.structured_models import LogQueryInput

logger = logging.getLogger("langgraph_agent.tools.log_tools")


async def query_incident_logs(
    project_id: str,
    incident_id: Optional[str] = None,
    service: Optional[str] = None,
    level: Optional[str] = None,
    keyword: Optional[str] = None,
    error_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """Queries PostgreSQL structured log records safely with bounds & parameterized SQL."""
    # Sanitize limit
    limit = max(1, min(limit, 200))
    
    # Try real PostgreSQL or fallback to structured mock query if DB connection fails
    try:
        engine = create_async_engine(config.DATABASE_URL, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            conditions = ["project_id = :project_id"]
            params: Dict[str, Any] = {"project_id": project_id, "limit": limit}
            
            if incident_id:
                conditions.append("(incident_id = :incident_id OR incident_id IS NULL)")
                params["incident_id"] = incident_id
                
            if service:
                conditions.append("LOWER(service) = LOWER(:service)")
                params["service"] = service
                
            if level:
                conditions.append("LOWER(level) = LOWER(:level)")
                params["level"] = level
                
            if keyword:
                conditions.append("(LOWER(message) LIKE :keyword OR LOWER(raw_line) LIKE :keyword)")
                params["keyword"] = f"%{keyword.lower()}%"
                
            if error_type:
                conditions.append("(LOWER(error_type) LIKE :error_type OR LOWER(message) LIKE :error_type)")
                params["error_type"] = f"%{error_type.lower()}%"

            where_clause = " AND ".join(conditions)
            sql = f"SELECT id, incident_id, project_id, timestamp, level, service, message, source, raw_line FROM log_records WHERE {where_clause} ORDER BY timestamp DESC LIMIT :limit"
            
            result = await session.execute(text(sql), params)
            rows = result.fetchall()
            
            records = [
                {
                    "id": row.id,
                    "incident_id": row.incident_id,
                    "project_id": row.project_id,
                    "timestamp": str(row.timestamp),
                    "level": row.level,
                    "service": row.service,
                    "message": row.message,
                    "source": row.source,
                }
                for row in rows
            ]
            
            await engine.dispose()
            return {
                "success": True,
                "total_matches": len(records),
                "query": {
                    "project_id": project_id,
                    "service": service,
                    "level": level,
                    "keyword": keyword,
                    "limit": limit,
                },
                "records": records,
            }
            
    except Exception as e:
        logger.error(f"Database log query failed for project '{project_id}': {e}")
        return {
            "success": False,
            "error_type": "DATABASE_CONNECTION_ERROR",
            "message": f"Unable to query PostgreSQL log records for service '{service or 'all'}': {e}",
            "total_matches": 0,
            "query": {
                "project_id": project_id,
                "service": service,
                "level": level,
                "keyword": keyword,
                "limit": limit,
            },
            "records": [],
        }
