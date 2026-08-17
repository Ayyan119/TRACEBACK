from typing import List, Optional
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.dependencies.user import get_current_user
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import user_service

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current Authenticated User Profile",
    description="Retrieves current user identity profile. Never returns raw secret API keys.",
)
async def get_me(
    current_user: UserModel = Depends(get_current_user),
) -> UserResponse:
    """Returns current user response."""
    return user_service.to_user_response(current_user)


@router.post(
    "/profile",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or Update User Profile & API Key",
    description="Saves user name, role, and securely encrypts optional OpenAI API key at rest.",
)
async def save_profile(
    user_in: UserCreate,
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Saves user profile attributes and encrypted API key."""
    return await user_service.create_or_update_profile(db, user_in, user_id=x_user_id)


@router.get(
    "/all",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List All Users (Multi-User Testing)",
    description="Retrieves all registered user profiles to support development identity switching.",
)
async def list_all_users(
    db: AsyncSession = Depends(get_db),
) -> List[UserResponse]:
    """Returns all registered user profiles."""
    return await user_service.get_all_users(db)
