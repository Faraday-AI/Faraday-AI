"""
User Profile Schemas

This module defines Pydantic schemas for user profile management.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class UserProfileBase(BaseModel):
    """Base user profile schema."""
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    timezone: Optional[str] = Field("UTC", description="User timezone")
    language: Optional[str] = Field("en", description="User language preference")
    notification_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="User notification preferences"
    )
    custom_settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom user settings"
    )


class UserProfileCreate(UserProfileBase):
    """Schema for creating a user profile."""
    pass


class UserProfileUpdate(BaseModel):
    """Schema for updating a user profile."""
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    timezone: Optional[str] = Field(None, description="User timezone")
    language: Optional[str] = Field(None, description="User language preference")
    notification_preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="User notification preferences"
    )
    custom_settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom user settings"
    )


class UserProfileResponse(UserProfileBase):
    """Schema for user profile responses."""
    id: int
    user_id: int
    avatar_url: Optional[str] = Field(None, description="Profile picture URL")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfilePrivacySettings(BaseModel):
    """Schema for user privacy settings."""
    profile_visibility: str = Field("public", description="Profile visibility level")
    show_email: bool = Field(False, description="Show email to other users")
    show_bio: bool = Field(True, description="Show biography to other users")
    show_activity: bool = Field(True, description="Show activity to other users")
    allow_messages: bool = Field(True, description="Allow messages from other users")
    show_online_status: bool = Field(True, description="Show online status")
    data_sharing: bool = Field(False, description="Allow data sharing for analytics")


class UserProfileNotificationSettings(BaseModel):
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
            "marketing": False
        },
        description="Specific notification type preferences"
    )


class UserProfileThemeSettings(BaseModel):
    """Schema for user theme settings."""
    theme: str = Field("light", description="UI theme preference")
    color_scheme: str = Field("default", description="Color scheme preference")
    font_size: str = Field("medium", description="Font size preference")
    high_contrast: bool = Field(False, description="High contrast mode")
    reduced_motion: bool = Field(False, description="Reduced motion preference")


class UserProfileAccessibilitySettings(BaseModel):
    """Schema for user accessibility settings."""
    screen_reader: bool = Field(False, description="Screen reader support")
    keyboard_navigation: bool = Field(True, description="Keyboard navigation support")
    high_contrast: bool = Field(False, description="High contrast mode")
    large_text: bool = Field(False, description="Large text mode")
    color_blind_friendly: bool = Field(False, description="Color blind friendly mode")


class UserProfileComplete(BaseModel):
    """Complete user profile with all settings."""
    id: int
    user_id: int
    bio: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    avatar_url: Optional[str] = None
    privacy_settings: UserProfilePrivacySettings
    notification_settings: UserProfileNotificationSettings
    theme_settings: UserProfileThemeSettings
    accessibility_settings: UserProfileAccessibilitySettings
    custom_settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileSearchResult(BaseModel):
    """Schema for user profile search results."""
    id: int
    user_id: int
    email: str
    first_name: str
    last_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileVerification(BaseModel):
    """Schema for user profile verification."""
    verification_type: str = Field(..., description="Type of verification")
    verification_data: Dict[str, Any] = Field(..., description="Verification data")
    verified: bool = Field(False, description="Verification status")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")


class UserProfileStats(BaseModel):
    """Schema for user profile statistics."""
    profile_views: int = Field(0, description="Number of profile views")
    last_profile_view: Optional[datetime] = Field(None, description="Last profile view")
    profile_completeness: float = Field(0.0, description="Profile completeness percentage")
    verification_status: str = Field("unverified", description="Verification status")
    member_since: datetime = Field(..., description="Member since date")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp") 