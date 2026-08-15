from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = "ok"
    version: Optional[str] = None
    environment: Optional[str] = None

    model_config = ConfigDict(frozen=True)


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list wrapper for API responses."""

    items: List[T]
    total: int
    page: int
    size: int
