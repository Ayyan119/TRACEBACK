import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import encrypt_api_key

logger = logging.getLogger("traceback.repositories.user")


class UserRepository:
    """Async repository for PostgreSQL CRUD operations on TRACEBACK Users."""

    async def get_by_id(self, db: AsyncSession, user_id: str) -> Optional[UserModel]:
        """Retrieves a single user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[UserModel]:
        """Retrieves a user by display name."""
        stmt = select(UserModel).where(UserModel.name == name.strip())
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all(self, db: AsyncSession) -> List[UserModel]:
        """Retrieves all users."""
        stmt = select(UserModel).order_by(UserModel.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def create(self, db: AsyncSession, user_in: UserCreate) -> UserModel:
        """Creates a new user record in PostgreSQL."""
        encrypted_key = None
        if user_in.openai_api_key and user_in.openai_api_key.strip():
            encrypted_key = encrypt_api_key(user_in.openai_api_key)

        user_orm = UserModel(
            name=user_in.name.strip(),
            role=user_in.role.strip(),
            encrypted_openai_api_key=encrypted_key,
        )
        db.add(user_orm)
        await db.commit()
        await db.refresh(user_orm)
        logger.info(f"Created new user '{user_orm.name}' ({user_orm.role}) [ID: {user_orm.id}]")
        return user_orm

    async def update(self, db: AsyncSession, user_orm: UserModel, user_in: UserUpdate) -> UserModel:
        """Updates user profile attributes and optional encrypted API key."""
        if user_in.name is not None and user_in.name.strip():
            user_orm.name = user_in.name.strip()
        if user_in.role is not None and user_in.role.strip():
            user_orm.role = user_in.role.strip()
        if user_in.openai_api_key is not None:
            if user_in.openai_api_key.strip():
                user_orm.encrypted_openai_api_key = encrypt_api_key(user_in.openai_api_key)
            else:
                user_orm.encrypted_openai_api_key = None

        db.add(user_orm)
        await db.commit()
        await db.refresh(user_orm)
        logger.info(f"Updated profile for user '{user_orm.name}' [ID: {user_orm.id}]")
        return user_orm


user_repository = UserRepository()
