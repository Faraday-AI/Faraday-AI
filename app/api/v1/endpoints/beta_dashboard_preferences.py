"""
API endpoints for Beta Dashboard Preferences Service (Phase 6)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
from app.services.pe.beta_dashboard_preferences_service import BetaDashboardPreferencesService

router = APIRouter(prefix="/beta/preferences", tags=["Beta Dashboard Preferences"])


def get_current_beta_teacher(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeacherRegistration:
    """Get the current beta teacher from the authenticated user."""
    teacher = db.query(TeacherRegistration).filter(
        TeacherRegistration.email == current_user.email,
        TeacherRegistration.is_active == True
    ).first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered beta teacher"
        )
    
    return teacher


@router.get("/widgets", response_model=List[dict])
async def get_beta_widgets(
    dashboard_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Get dashboard widgets for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.get_widgets(
        dashboard_id=dashboard_id,
        is_active=is_active,
        limit=limit
    )


@router.post("/widgets", response_model=dict)
async def create_beta_widget(
    widget_data: dict,
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Create a new dashboard widget for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.create_widget(widget_data)


@router.put("/widgets/{widget_id}", response_model=dict)
async def update_beta_widget(
    widget_id: int,
    widget_data: dict,
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Update a dashboard widget for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.update_widget(widget_id, widget_data)


@router.delete("/widgets/{widget_id}", response_model=dict)
async def delete_beta_widget(
    widget_id: int,
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Delete a dashboard widget for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.delete_widget(widget_id)


@router.get("/user-preferences", response_model=dict)
async def get_beta_user_preferences(
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Get user preferences for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.get_user_preferences()


@router.put("/user-preferences", response_model=dict)
async def update_beta_user_preferences(
    preferences: dict,
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Update user preferences for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.update_user_preferences(preferences=preferences)


@router.get("/notifications", response_model=List[dict])
async def get_beta_notification_preferences(
    channel: Optional[str] = None,
    limit: int = 100,
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Get notification preferences for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.get_notification_preferences(
        channel=channel,
        limit=limit
    )


@router.post("/notifications", response_model=dict)
async def create_beta_notification_preference(
    pref_data: dict,
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Create a new notification preference for beta teacher."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.create_notification_preference(pref_data)


@router.post("/migrate", response_model=dict)
async def migrate_beta_preferences(
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Migrate existing beta preferences data (Phase 6 migration)."""
    service = BetaDashboardPreferencesService(db, current_teacher.id)
    return await service.migrate_existing_preferences_data()

