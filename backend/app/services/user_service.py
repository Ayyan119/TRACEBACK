import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserModel
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.security import mask_api_key

logger = logging.getLogger("traceback.services.user")

DEFAULT_USER_ID = "usr_default_ayyan"


class UserService:
    """Business logic service for TRACEBACK user profile management."""

    def to_user_response(self, user: UserModel) -> UserResponse:
        """Converts UserModel ORM instance to safe UserResponse schema."""
        has_key = bool(user.encrypted_openai_api_key and user.encrypted_openai_api_key.strip())
        masked = mask_api_key(user.encrypted_openai_api_key) if has_key else None
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            has_openai_api_key=has_key,
            masked_api_key=masked,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def get_or_create_default_user(self, db: AsyncSession) -> UserModel:
        """Ensures the primary default user exists in PostgreSQL."""
        user = await user_repository.get_by_id(db, DEFAULT_USER_ID)
        if not user:
            user = await user_repository.get_by_name(db, "Ayyan Shahid")
        if not user:
            user_in = UserCreate(
                name="Ayyan Shahid",
                role="Senior Software Engineer",
            )
            user = await user_repository.create(db, user_in)
        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[UserModel]:
        """Fetches a user by ID with default fallback."""
        if not user_id or user_id.strip() in ("", "null", "undefined"):
            return await self.get_or_create_default_user(db)
        user = await user_repository.get_by_id(db, user_id)
        if not user:
            return await self.get_or_create_default_user(db)
        return user

    async def get_all_users(self, db: AsyncSession) -> List[UserResponse]:
        """Returns all registered users."""
        users = await user_repository.get_all(db)
        return [self.to_user_response(u) for u in users]

    async def create_or_update_profile(
        self, db: AsyncSession, user_in: UserCreate, user_id: Optional[str] = None
    ) -> UserResponse:
        """Creates or updates a user profile and encrypted API key."""
        target_user: Optional[UserModel] = None
        if user_id and user_id.strip() not in ("", "null", "undefined"):
            target_user = await user_repository.get_by_id(db, user_id)

        if not target_user:
            # Check by name first to avoid duplicates
            target_user = await user_repository.get_by_name(db, user_in.name)

        if target_user:
            update_dto = UserUpdate(
                name=user_in.name,
                role=user_in.role,
                openai_api_key=user_in.openai_api_key,
            )
            updated = await user_repository.update(db, target_user, update_dto)
            return self.to_user_response(updated)

        created = await user_repository.create(db, user_in)
        return self.to_user_response(created)


user_service = UserService()
