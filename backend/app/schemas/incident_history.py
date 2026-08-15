from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class IncidentHistoryResponse(BaseModel):
    """Pydantic schema for returning incident history record details."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    project_id: str
    incident_code: str
    historical_payload: Dict[str, Any]
    qdrant_point_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
