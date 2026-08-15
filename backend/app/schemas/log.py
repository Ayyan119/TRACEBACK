from datetime import datetime, date as date_type, time as time_type
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class LogRecordResponse(BaseModel):
    """Pydantic schema for structured log record API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    incident_id: Optional[str] = None
    file_id: Optional[str] = None
    timestamp: datetime
    date: date_type
    time: time_type
    day: str
    log_type: str
    level: str
    message: str
    source: Optional[str] = None
    service: Optional[str] = None
    raw_line: str
    parse_status: str
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
