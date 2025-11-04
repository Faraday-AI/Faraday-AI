"""Dependencies package for the dashboard API."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dashboard.services.access_control_service import AccessControlService
from app.dashboard.schemas.access_control import ResourceType, ActionType
from app.dashboard.dependencies.auth import get_current_user, get_auth_deps

# Re-export the auth dependencies
__all__ = ["get_current_user", "get_auth_deps"]

async def require_admin(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> bool:
    """Require admin privileges for the current user."""
    access_control = AccessControlService(db)
    has_permission = await access_control.check_permission(
        user_id=user_id,
        resource_type=ResourceType.SYSTEM,
        action=ActionType.ADMINISTER
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return True 