"""
API endpoints for Dashboard Preferences Service (Phase 6)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.dashboard.services.dashboard_preferences_service import DashboardPreferencesService

router = APIRouter(prefix="/dashboard/preferences", tags=["Dashboard Preferences"])


@router.get("/widgets", response_model=List[dict])
async def get_widgets(
    user_id: Optional[int] = None,
    dashboard_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard widgets."""
    service = DashboardPreferencesService(db)
    return await service.get_widgets(
        user_id=user_id,
        dashboard_id=dashboard_id,
        is_active=is_active,
        limit=limit
    )


@router.post("/widgets", response_model=dict)
async def create_widget(
    widget_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new dashboard widget."""
    service = DashboardPreferencesService(db)
    return await service.create_widget(widget_data)


@router.put("/widgets/{widget_id}", response_model=dict)
async def update_widget(
    widget_id: int,
    widget_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a dashboard widget."""
    service = DashboardPreferencesService(db)
    return await service.update_widget(widget_id, widget_data)


@router.delete("/widgets/{widget_id}", response_model=dict)
async def delete_widget(
    widget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a dashboard widget."""
    service = DashboardPreferencesService(db)
    return await service.delete_widget(widget_id)


@router.get("/user-preferences/{user_id}", response_model=dict)
async def get_user_preferences(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences."""
    service = DashboardPreferencesService(db)
    return await service.get_user_preferences(user_id)


@router.put("/user-preferences/{user_id}", response_model=dict)
async def update_user_preferences(
    user_id: int,
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences."""
    service = DashboardPreferencesService(db)
    return await service.update_user_preferences(user_id, preferences)


@router.get("/notifications/{user_id}", response_model=List[dict])
async def get_notification_preferences(
    user_id: int,
    channel: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences for a user."""
    service = DashboardPreferencesService(db)
    return await service.get_notification_preferences(
        user_id=user_id,
        channel=channel,
        limit=limit
    )


@router.post("/notifications", response_model=dict)
async def create_notification_preference(
    pref_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification preference."""
    service = DashboardPreferencesService(db)
    return await service.create_notification_preference(pref_data)


@router.post("/migrate", response_model=dict)
async def migrate_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Migrate existing preferences data (Phase 6 migration)."""
    service = DashboardPreferencesService(db)
    return await service.migrate_existing_preferences_data()

