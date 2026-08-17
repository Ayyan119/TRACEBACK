from typing import Optional
from fastapi import Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.common import get_db
from app.models.user import UserModel
from app.services.user_service import user_service


async def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    """
    FastAPI dependency that resolves the authenticated UserModel for the current request.
    Reads X-User-ID header. If missing/invalid, falls back gracefully to default initial user.
    """
    if x_user_id and x_user_id.strip() not in ("", "null", "undefined"):
        return await user_service.get_user_by_id(db, x_user_id.strip(), name=x_user_name, role=x_user_role)

    # If X-User-Name is provided, attempt lookup or default
    if x_user_name and x_user_name.strip():
        from app.repositories.user_repository import user_repository
        user = await user_repository.get_by_name(db, x_user_name.strip())
        if user:
            return user

    # Default fallback
    return await user_service.get_or_create_default_user(db)
