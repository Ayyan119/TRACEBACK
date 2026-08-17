from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ResourceNotFoundException, PermissionDeniedException
from app.services.project_service import project_service


async def validate_project_access(
    db: AsyncSession, project_id: str, user_id: str
) -> None:
    """
    Validates that target project_id exists and belongs to current user_id.
    If not owned by user, raises 404/403 to prevent cross-user data leakage.
    """
    if not project_id:
        return
    project = await project_service.get_project_by_id(db, project_id, user_id=user_id)
    if not project:
        raise ResourceNotFoundException("Project", project_id)
