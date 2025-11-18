from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict
from app.db.session import get_db
from app.dashboard.services.user_preferences_service import UserPreferencesService
from app.dashboard.schemas.user_preferences import (
    UserPreferencesResponse,
    UserPreferencesUpdate
)
from app.dashboard.dependencies.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user preferences."""
    try:
        service = UserPreferencesService(db)
        return await service.get_preferences(current_user["id"])
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving preferences"
        )

@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_preferences(
    preferences: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user preferences."""
    try:
        service = UserPreferencesService(db)
        return await service.update_preferences(
            user_id=current_user["id"],
            preferences_update=preferences
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error updating preferences"
        )

@router.post("/preferences/reset", response_model=UserPreferencesResponse)
async def reset_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reset user preferences to defaults."""
    try:
        service = UserPreferencesService(db)
        return await service.reset_preferences(current_user["id"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error resetting preferences"
        )

@router.get("/preferences/export")
async def export_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export user preferences as JSON."""
    try:
        service = UserPreferencesService(db)
        return await service.export_preferences(current_user["id"])
    except Exception as e:
        logger.error(f"Error exporting preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error exporting preferences"
        )

@router.post("/preferences/import", response_model=UserPreferencesResponse)
async def import_preferences(
    preferences_data: Dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Import user preferences from JSON."""
    try:
        service = UserPreferencesService(db)
        return await service.import_preferences(
            user_id=current_user["id"],
            preferences_data=preferences_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error importing preferences"
        )

@router.post("/preferences/validate")
async def validate_preferences(
    preferences_data: Dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Validate preferences data."""
    try:
        service = UserPreferencesService(db)
        return await service.validate_preferences(preferences_data)
    except Exception as e:
        logger.error(f"Error validating preferences: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error validating preferences"
        ) 