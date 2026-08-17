import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserModel
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.security import mask_api_key

logger = logging.getLogger("traceback.services.user")

DEFAULT_USER_ID = "usr_default_ayyan"


from app.repositories.project_repository import project_repository
from app.schemas.project import ProjectCreate

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
        """Ensures default preset users exist in PostgreSQL."""
        user = await user_repository.get_by_id(db, DEFAULT_USER_ID)
        if not user:
            user = await user_repository.get_by_name(db, "Ayyan Shahid")
        if not user:
            user_in = UserCreate(
                name="Ayyan Shahid",
                role="AI Engineer",
            )
            user = await user_repository.create(db, user_in)

        # Ensure Guest Tester account exists for instant testing
        guest = await user_repository.get_by_name(db, "Guest Tester")
        if not guest:
            await user_repository.create(
                db, UserCreate(name="Guest Tester", role="Guest Tester")
            )

        # Seed default sample projects if Ayyan Shahid currently has 0 projects in PostgreSQL
        try:
            existing_projects = await project_repository.get_all(db, user_id=user.id)
            if len(existing_projects) == 0:
                logger.info(f"Seeding default workspace projects for {user.name} ({user.id})...")
                samples = [
                    {
                        "name": "NovaStream Production",
                        "slug": "novastream-production",
                        "environment": "production",
                        "description": "Core real-time video streaming & microservice transcoding platform.",
                        "owner_team": "Core Platform Engineering",
                    },
                    {
                        "name": "ShopFlow",
                        "slug": "shopflow",
                        "environment": "production",
                        "description": "E-commerce checkout & inventory management microservice stack.",
                        "owner_team": "Commerce Team",
                    },
                    {
                        "name": "FinBank Platform",
                        "slug": "finbank-platform",
                        "environment": "staging",
                        "description": "Financial ledger & payment transaction processing pipeline.",
                        "owner_team": "FinTech Core",
                    },
                ]
                for sp in samples:
                    await project_repository.create(
                        db,
                        ProjectCreate(
                            name=sp["name"],
                            environment=sp["environment"],
                            description=sp["description"],
                            ownerTeam=sp["owner_team"],
                        ),
                        slug=sp["slug"],
                        user_id=user.id,
                    )
                logger.info("Default workspace projects seeded successfully.")
        except Exception as seed_err:
            logger.warning(f"Project seed check skipped: {seed_err}")

        return user

    async def get_user_by_id(
        self, db: AsyncSession, user_id: str, name: Optional[str] = None, role: Optional[str] = None
    ) -> UserModel:
        """Fetches a user by ID. If user doesn't exist yet, creates isolated record for this user_id."""
        if not user_id or user_id.strip() in ("", "null", "undefined"):
            return await self.get_or_create_default_user(db)

        user = await user_repository.get_by_id(db, user_id)
        if user:
            return user

        # Check by name to avoid duplicates
        if name and name.strip():
            user = await user_repository.get_by_name(db, name.strip())
            if user:
                return user

        # Create an isolated user record for this new/guest user_id
        user_name = name.strip() if name and name.strip() else f"User-{user_id[-6:]}"
        user_role = role.strip() if role and role.strip() else "Guest Tester"

        new_user = UserModel(
            id=user_id,
            name=user_name,
            role=user_role,
        )
        db.add(new_user)
        await db.flush()
        await db.refresh(new_user)
        return new_user

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
