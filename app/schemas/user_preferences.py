"""
User Preferences Schemas

This module defines Pydantic schemas for user preferences management.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ThemeSettings(BaseModel):
    """Schema for user theme settings."""
    theme: str = Field("light", description="UI theme preference")
    color_scheme: str = Field("default", description="Color scheme preference")
    font_size: str = Field("medium", description="Font size preference")
    high_contrast: bool = Field(False, description="High contrast mode")
    reduced_motion: bool = Field(False, description="Reduced motion preference")
    custom_colors: Optional[Dict[str, str]] = Field(None, description="Custom color overrides")


class NotificationSettings(BaseModel):
    """Schema for user notification settings."""
    email_notifications: bool = Field(True, description="Enable email notifications")
    push_notifications: bool = Field(True, description="Enable push notifications")
    sms_notifications: bool = Field(False, description="Enable SMS notifications")
    notification_frequency: str = Field("immediate", description="Notification frequency")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start time")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end time")
    notification_types: Dict[str, bool] = Field(
        default_factory=lambda: {
            "security_alerts": True,
            "activity_updates": True,
            "system_notifications": True,
            "marketing": False,
            "educational_content": True,
            "peer_interactions": True
        },
        description="Specific notification type preferences"
    )


class AccessibilitySettings(BaseModel):
    """Schema for user accessibility settings."""
    screen_reader: bool = Field(False, description="Screen reader support")
    keyboard_navigation: bool = Field(True, description="Keyboard navigation support")
    high_contrast: bool = Field(False, description="High contrast mode")
    large_text: bool = Field(False, description="Large text mode")
    color_blind_friendly: bool = Field(False, description="Color blind friendly mode")
    focus_indicators: bool = Field(True, description="Enhanced focus indicators")
    alt_text_preference: str = Field("auto", description="Alt text preference")


class LanguageSettings(BaseModel):
    """Schema for user language and regional settings."""
    language: str = Field("en", description="Primary language")
    timezone: str = Field("UTC", description="User timezone")
    date_format: str = Field("MM/DD/YYYY", description="Date format preference")
    time_format: str = Field("12h", description="Time format preference")
    currency: str = Field("USD", description="Currency preference")
    number_format: str = Field("en-US", description="Number format preference")


class UserPreferencesBase(BaseModel):
    """Base user preferences schema."""
    theme: Optional[ThemeSettings] = None
    notifications: Optional[NotificationSettings] = None
    accessibility: Optional[AccessibilitySettings] = None
    language: Optional[str] = Field("en", description="User language preference")
    timezone: Optional[str] = Field("UTC", description="User timezone")


class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences."""
    pass


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    theme: Optional[ThemeSettings] = None
    notifications: Optional[NotificationSettings] = None
    accessibility: Optional[AccessibilitySettings] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences responses."""
    user_id: int
    
    class Config:
        from_attributes = True


class UserPreferencesComplete(BaseModel):
    """Complete user preferences with all settings."""
    user_id: int
    theme: ThemeSettings
    notifications: NotificationSettings
    accessibility: AccessibilitySettings
    language: str
    timezone: str
    
    class Config:
        from_attributes = True


class UserPreferencesExport(BaseModel):
    """Schema for user preferences export."""
    user_id: int
    exported_at: str
    preferences: Dict[str, Any]
    version: str = Field("1.0", description="Export format version")


class UserPreferencesImport(BaseModel):
    """Schema for user preferences import."""
    preferences: Dict[str, Any]
    version: str = Field("1.0", description="Import format version")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing preferences")


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating specific notification preferences."""
    notification_type: str = Field(..., description="Type of notification to update")
    enabled: bool = Field(..., description="Whether the notification type is enabled")


class ThemePreferenceUpdate(BaseModel):
    """Schema for updating specific theme preferences."""
    setting: str = Field(..., description="Theme setting to update")
    value: Any = Field(..., description="New value for the setting")


class AccessibilityPreferenceUpdate(BaseModel):
    """Schema for updating specific accessibility preferences."""
    setting: str = Field(..., description="Accessibility setting to update")
    value: bool = Field(..., description="New value for the setting")


class UserPreferencesSummary(BaseModel):
    """Summary of user preferences."""
    user_id: int
    has_custom_theme: bool
    has_custom_notifications: bool
    has_accessibility_settings: bool
    language: str
    timezone: str
    last_updated: str
    
    class Config:
        from_attributes = True 