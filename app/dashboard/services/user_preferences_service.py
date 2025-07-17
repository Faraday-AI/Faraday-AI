from typing import Dict, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.dashboard.models.user_preferences import UserPreferences
from app.dashboard.schemas.user_preferences import (
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse
)
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class UserPreferencesService:
    """Service for managing user preferences."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_preferences(self, user_id: str) -> UserPreferencesResponse:
        """Get user preferences."""
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not preferences:
            # Create default preferences if none exist
            preferences = await self.create_default_preferences(user_id)
        
        return UserPreferencesResponse.from_orm(preferences)
    
    async def create_default_preferences(self, user_id: str) -> UserPreferences:
        """Create default preferences for a user."""
        preferences = UserPreferences(
            user_id=user_id
        )
        self.db.add(preferences)
        self.db.commit()
        self.db.refresh(preferences)
        return preferences
    
    async def update_preferences(
        self,
        user_id: str,
        preferences_update: UserPreferencesUpdate
    ) -> UserPreferencesResponse:
        """Update user preferences."""
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not preferences:
            raise HTTPException(
                status_code=404,
                detail="User preferences not found"
            )
        
        # Update preferences
        update_data = preferences_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)
        
        preferences.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(preferences)
        
        return UserPreferencesResponse.from_orm(preferences)
    
    async def reset_preferences(self, user_id: str) -> UserPreferencesResponse:
        """Reset user preferences to defaults."""
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not preferences:
            raise HTTPException(
                status_code=404,
                detail="User preferences not found"
            )
        
        # Create new default preferences
        default_preferences = UserPreferences()
        for field in UserPreferences.__table__.columns:
            if field.name not in ['id', 'user_id', 'created_at', 'updated_at']:
                setattr(preferences, field.name, getattr(default_preferences, field.name))
        
        preferences.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(preferences)
        
        return UserPreferencesResponse.from_orm(preferences)
    
    async def export_preferences(self, user_id: str) -> Dict:
        """Export user preferences as JSON."""
        preferences = await self.get_preferences(user_id)
        return preferences.dict()
    
    async def import_preferences(self, user_id: str, preferences_data: Dict) -> UserPreferencesResponse:
        """Import user preferences from JSON."""
        try:
            # Validate the imported data
            UserPreferencesUpdate(**preferences_data)
            
            # Update preferences
            preferences = self.db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                preferences = UserPreferences(user_id=user_id)
                self.db.add(preferences)
            
            for field, value in preferences_data.items():
                setattr(preferences, field, value)
            
            preferences.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(preferences)
            
            return UserPreferencesResponse.from_orm(preferences)
            
        except Exception as e:
            logger.error(f"Error importing preferences: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid preferences data"
            )
    
    async def validate_preferences(self, preferences_data: Dict) -> Dict:
        """Validate preferences data."""
        try:
            UserPreferencesUpdate(**preferences_data)
            return {"valid": True, "errors": []}
        except Exception as e:
            return {"valid": False, "errors": [str(e)]} 