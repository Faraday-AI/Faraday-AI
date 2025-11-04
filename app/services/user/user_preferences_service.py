"""
User Preferences Service

This module provides comprehensive user preferences management functionality
including theme settings, notification preferences, language settings, and accessibility preferences.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends

from app.models.core.user import User
from app.models.user_management.user.user_management import UserProfile
from app.schemas.user_preferences import (
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse,
    ThemeSettings,
    NotificationSettings,
    AccessibilitySettings
)
from app.db.session import get_db


class UserPreferencesService:
    """Service for managing user preferences."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return None
        
        return {
            "theme": profile.custom_settings.get("theme", {}) if profile.custom_settings else {},
            "notifications": profile.notification_preferences or {},
            "accessibility": profile.custom_settings.get("accessibility", {}) if profile.custom_settings else {},
            "language": profile.language,
            "timezone": profile.timezone
        }
    
    async def update_user_preferences(self, user_id: int, preferences_data: UserPreferencesUpdate) -> Dict[str, Any]:
        """Update user preferences."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            # Create profile if it doesn't exist
            profile = UserProfile(
                user_id=user_id,
                timezone="UTC",
                language="en",
                notification_preferences={},
                custom_settings={}
            )
            self.db.add(profile)
        
        # Update preferences
        update_data = preferences_data.dict(exclude_unset=True)
        
        if "theme" in update_data:
            if not profile.custom_settings:
                profile.custom_settings = {}
            profile.custom_settings["theme"] = update_data["theme"]
        
        if "notifications" in update_data:
            profile.notification_preferences = update_data["notifications"]
        
        if "accessibility" in update_data:
            if not profile.custom_settings:
                profile.custom_settings = {}
            profile.custom_settings["accessibility"] = update_data["accessibility"]
        
        if "language" in update_data:
            profile.language = update_data["language"]
        
        if "timezone" in update_data:
            profile.timezone = update_data["timezone"]
        
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return await self.get_user_preferences(user_id)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update user preferences")
    
    async def update_theme_settings(self, user_id: int, theme_settings: ThemeSettings) -> Dict[str, Any]:
        """Update user theme settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        if not profile.custom_settings:
            profile.custom_settings = {}
        profile.custom_settings["theme"] = theme_settings.dict()
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return profile.custom_settings["theme"]
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update theme settings")
    
    async def get_theme_settings(self, user_id: int) -> ThemeSettings:
        """Get user theme settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        theme_data = profile.custom_settings.get("theme", {}) if profile.custom_settings else {}
        
        # Handle case where theme_data might be a string (e.g., "dark") instead of a dict
        if isinstance(theme_data, str):
            return ThemeSettings(theme=theme_data)
        elif isinstance(theme_data, dict):
            return ThemeSettings(**theme_data) if theme_data else ThemeSettings()
        else:
            return ThemeSettings()
    
    async def update_notification_settings(self, user_id: int, notification_settings: NotificationSettings) -> Dict[str, Any]:
        """Update user notification settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile.notification_preferences = notification_settings.dict()
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return profile.notification_preferences
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update notification settings")
    
    async def get_notification_settings(self, user_id: int) -> NotificationSettings:
        """Get user notification settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        notification_data = profile.notification_preferences or {}
        return NotificationSettings(**notification_data)
    
    async def update_accessibility_settings(self, user_id: int, accessibility_settings: AccessibilitySettings) -> Dict[str, Any]:
        """Update user accessibility settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        if not profile.custom_settings:
            profile.custom_settings = {}
        profile.custom_settings["accessibility"] = accessibility_settings.dict()
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return profile.custom_settings["accessibility"]
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update accessibility settings")
    
    async def get_accessibility_settings(self, user_id: int) -> AccessibilitySettings:
        """Get user accessibility settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        accessibility_data = profile.custom_settings.get("accessibility", {}) if profile.custom_settings else {}
        
        # Handle case where accessibility_data might be a boolean or string instead of a dict
        if isinstance(accessibility_data, bool):
            return AccessibilitySettings(high_contrast=accessibility_data)
        elif isinstance(accessibility_data, dict):
            return AccessibilitySettings(**accessibility_data) if accessibility_data else AccessibilitySettings()
        else:
            return AccessibilitySettings()
    
    async def update_language_settings(self, user_id: int, language: str, timezone: str) -> Dict[str, str]:
        """Update user language and timezone settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile.language = language
        profile.timezone = timezone
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return {"language": profile.language, "timezone": profile.timezone}
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update language settings")
    
    async def get_language_settings(self, user_id: int) -> Dict[str, str]:
        """Get user language and timezone settings."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {"language": profile.language, "timezone": profile.timezone}
    
    async def reset_preferences_to_default(self, user_id: int) -> Dict[str, Any]:
        """Reset user preferences to default values."""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Reset to default values
        profile.language = "en"
        profile.timezone = "UTC"
        profile.notification_preferences = {
            "email_notifications": True,
            "push_notifications": True,
            "sms_notifications": False,
            "notification_frequency": "immediate",
            "notification_types": {
                "security_alerts": True,
                "activity_updates": True,
                "system_notifications": True,
                "marketing": False
            }
        }
        
        if profile.custom_settings:
            profile.custom_settings["theme"] = {
                "theme": "light",
                "color_scheme": "default",
                "font_size": "medium",
                "high_contrast": False,
                "reduced_motion": False
            }
            profile.custom_settings["accessibility"] = {
                "screen_reader": False,
                "keyboard_navigation": True,
                "high_contrast": False,
                "large_text": False,
                "color_blind_friendly": False
            }
        
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return await self.get_user_preferences(user_id)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to reset preferences")
    
    async def export_preferences(self, user_id: int) -> Dict[str, Any]:
        """Export user preferences for backup."""
        preferences = await self.get_user_preferences(user_id)
        if not preferences:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        return {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "preferences": preferences
        }
    
    async def import_preferences(self, user_id: int, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import user preferences from backup."""
        if "preferences" not in preferences_data:
            raise HTTPException(status_code=400, detail="Invalid preferences data")
        
        preferences = preferences_data["preferences"]
        
        # Update preferences
        update_data = UserPreferencesUpdate(**preferences)
        return await self.update_user_preferences(user_id, update_data)


def get_user_preferences_service(db: Session = Depends(get_db)) -> UserPreferencesService:
    """Dependency to get user preferences service."""
    return UserPreferencesService(db) 