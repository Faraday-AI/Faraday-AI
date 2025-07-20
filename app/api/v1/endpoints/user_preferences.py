"""
User Preferences API Endpoints

This module provides API endpoints for user preferences management.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.services.user.user_preferences_service import UserPreferencesService, get_user_preferences_service
from app.schemas.user_preferences import (
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse,
    UserPreferencesComplete,
    ThemeSettings,
    NotificationSettings,
    AccessibilitySettings,
    NotificationPreferenceUpdate,
    ThemePreferenceUpdate,
    AccessibilityPreferenceUpdate,
    UserPreferencesSummary
)

router = APIRouter()


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Get current user's preferences."""
    preferences = await preferences_service.get_user_preferences(current_user.id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    return UserPreferencesResponse(user_id=current_user.id, **preferences)


@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update user preferences."""
    preferences = await preferences_service.update_user_preferences(current_user.id, preferences_data)
    return UserPreferencesResponse(user_id=current_user.id, **preferences)


@router.get("/preferences/complete", response_model=UserPreferencesComplete)
async def get_complete_preferences(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Get complete user preferences with all settings."""
    preferences = await preferences_service.get_user_preferences(current_user.id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    return UserPreferencesComplete(
        user_id=current_user.id,
        theme=ThemeSettings(**preferences.get("theme", {})),
        notifications=NotificationSettings(**preferences.get("notifications", {})),
        accessibility=AccessibilitySettings(**preferences.get("accessibility", {})),
        language=preferences.get("language", "en"),
        timezone=preferences.get("timezone", "UTC")
    )


@router.get("/preferences/theme", response_model=ThemeSettings)
async def get_theme_settings(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Get user theme settings."""
    return await preferences_service.get_theme_settings(current_user.id)


@router.put("/preferences/theme", response_model=Dict[str, Any])
async def update_theme_settings(
    theme_settings: ThemeSettings,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update user theme settings."""
    return await preferences_service.update_theme_settings(current_user.id, theme_settings)


@router.patch("/preferences/theme")
async def update_theme_preference(
    theme_update: ThemePreferenceUpdate,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update specific theme preference."""
    current_theme = await preferences_service.get_theme_settings(current_user.id)
    theme_dict = current_theme.dict()
    theme_dict[theme_update.setting] = theme_update.value
    
    updated_theme = ThemeSettings(**theme_dict)
    return await preferences_service.update_theme_settings(current_user.id, updated_theme)


@router.get("/preferences/notifications", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Get user notification settings."""
    return await preferences_service.get_notification_settings(current_user.id)


@router.put("/preferences/notifications", response_model=Dict[str, Any])
async def update_notification_settings(
    notification_settings: NotificationSettings,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update user notification settings."""
    return await preferences_service.update_notification_settings(current_user.id, notification_settings)


@router.patch("/preferences/notifications")
async def update_notification_preference(
    notification_update: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update specific notification preference."""
    current_notifications = await preferences_service.get_notification_settings(current_user.id)
    notification_dict = current_notifications.dict()
    
    if notification_update.notification_type in notification_dict["notification_types"]:
        notification_dict["notification_types"][notification_update.notification_type] = notification_update.enabled
    else:
        notification_dict[notification_update.notification_type] = notification_update.enabled
    
    updated_notifications = NotificationSettings(**notification_dict)
    return await preferences_service.update_notification_settings(current_user.id, updated_notifications)


@router.get("/preferences/accessibility", response_model=AccessibilitySettings)
async def get_accessibility_settings(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Get user accessibility settings."""
    return await preferences_service.get_accessibility_settings(current_user.id)


@router.put("/preferences/accessibility", response_model=Dict[str, Any])
async def update_accessibility_settings(
    accessibility_settings: AccessibilitySettings,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update user accessibility settings."""
    return await preferences_service.update_accessibility_settings(current_user.id, accessibility_settings)


@router.patch("/preferences/accessibility")
async def update_accessibility_preference(
    accessibility_update: AccessibilityPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update specific accessibility preference."""
    current_accessibility = await preferences_service.get_accessibility_settings(current_user.id)
    accessibility_dict = current_accessibility.dict()
    accessibility_dict[accessibility_update.setting] = accessibility_update.value
    
    updated_accessibility = AccessibilitySettings(**accessibility_dict)
    return await preferences_service.update_accessibility_settings(current_user.id, updated_accessibility)


@router.get("/preferences/language", response_model=Dict[str, str])
async def get_language_settings(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Get user language and timezone settings."""
    return await preferences_service.get_language_settings(current_user.id)


@router.put("/preferences/language", response_model=Dict[str, str])
async def update_language_settings(
    language: str,
    timezone: str,
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Update user language and timezone settings."""
    return await preferences_service.update_language_settings(current_user.id, language, timezone)


@router.post("/preferences/reset", response_model=UserPreferencesResponse)
async def reset_preferences_to_default(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Reset user preferences to default values."""
    preferences = await preferences_service.reset_preferences_to_default(current_user.id)
    return UserPreferencesResponse(user_id=current_user.id, **preferences)


@router.get("/preferences/export", response_model=Dict[str, Any])
async def export_preferences(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Export user preferences for backup."""
    return await preferences_service.export_preferences(current_user.id)


@router.post("/preferences/import", response_model=UserPreferencesResponse)
async def import_preferences(
    preferences_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Import user preferences from backup."""
    preferences = await preferences_service.import_preferences(current_user.id, preferences_data)
    return UserPreferencesResponse(user_id=current_user.id, **preferences)


@router.get("/preferences/summary", response_model=UserPreferencesSummary)
async def get_preferences_summary(
    current_user: User = Depends(get_current_user),
    preferences_service: UserPreferencesService = Depends(get_user_preferences_service)
):
    """Get summary of user preferences."""
    preferences = await preferences_service.get_user_preferences(current_user.id)
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    return UserPreferencesSummary(
        user_id=current_user.id,
        has_custom_theme=bool(preferences.get("theme")),
        has_custom_notifications=bool(preferences.get("notifications")),
        has_accessibility_settings=bool(preferences.get("accessibility")),
        language=preferences.get("language", "en"),
        timezone=preferences.get("timezone", "UTC"),
        last_updated=preferences.get("last_updated", "")
    ) 