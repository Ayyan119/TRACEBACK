from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Schema for creating or onboarding a new user profile."""
    name: str = Field(..., min_length=1, max_length=128, description="Display name of the user")
    role: str = Field(..., min_length=1, max_length=128, description="Technical role of the user")
    openai_api_key: Optional[str] = Field(None, description="Optional sensitive OpenAI API Key")


class UserUpdate(BaseModel):
    """Schema for updating an existing user profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    role: Optional[str] = Field(None, min_length=1, max_length=128)
    openai_api_key: Optional[str] = Field(None, description="Optional sensitive OpenAI API Key to update")


class UserResponse(BaseModel):
    """Schema for user profile responses returned to the frontend. Never includes raw API key."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique internal user identity ID")
    name: str = Field(..., description="Display name of the user")
    role: str = Field(..., description="Technical role of the user")
    has_openai_api_key: bool = Field(False, description="True if an OpenAI API key is securely configured")
    masked_api_key: Optional[str] = Field(None, description="Masked representation (••••••••••••••••) if configured")
    created_at: datetime
    updated_at: datetime
