from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class FontSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class TimeFormat(str, Enum):
    HOUR_12 = "12h"
    HOUR_24 = "24h"

class BackupFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class UserPreferencesBase(BaseModel):
    """Base schema for user preferences."""
    theme: Theme = Field(default=Theme.LIGHT, description="UI theme preference")
    accent_color: Optional[str] = Field(None, description="Custom accent color")
    font_size: FontSize = Field(default=FontSize.MEDIUM, description="Font size preference")
    font_family: Optional[str] = Field("system", description="Font family preference")
    
    dashboard_layout: Optional[Dict] = Field(None, description="Custom dashboard layout")
    sidebar_position: str = Field(default="left", description="Sidebar position (left/right)")
    sidebar_collapsed: bool = Field(default=False, description="Whether sidebar is collapsed")
    grid_view: bool = Field(default=True, description="Use grid view instead of list view")
    
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    push_notifications: bool = Field(default=True, description="Enable push notifications")
    in_app_notifications: bool = Field(default=True, description="Enable in-app notifications")
    notification_sound: bool = Field(default=True, description="Enable notification sounds")
    notification_types: List[str] = Field(default_factory=list, description="Types of notifications to receive")
    quiet_hours: List[Dict[str, str]] = Field(default_factory=list, description="Time ranges for quiet hours")
    
    language: str = Field(default="en", description="Preferred language")
    timezone: str = Field(default="UTC", description="Preferred timezone")
    date_format: str = Field(default="YYYY-MM-DD", description="Date format preference")
    time_format: TimeFormat = Field(default=TimeFormat.HOUR_24, description="Time format preference")
    
    data_sharing: bool = Field(default=False, description="Allow data sharing")
    analytics_opt_in: bool = Field(default=True, description="Opt-in for analytics")
    personalized_ads: bool = Field(default=False, description="Allow personalized ads")
    
    high_contrast: bool = Field(default=False, description="Enable high contrast mode")
    reduced_motion: bool = Field(default=False, description="Reduce motion effects")
    screen_reader: bool = Field(default=False, description="Enable screen reader support")
    keyboard_shortcuts: Dict[str, str] = Field(default_factory=dict, description="Custom keyboard shortcuts")
    
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_duration: int = Field(default=300, ge=60, le=3600, description="Cache duration in seconds")
    auto_refresh: bool = Field(default=True, description="Enable auto-refresh")
    refresh_interval: int = Field(default=60, ge=30, le=300, description="Refresh interval in seconds")
    
    connected_services: List[str] = Field(default_factory=list, description="Connected third-party services")
    webhook_urls: Dict[str, str] = Field(default_factory=dict, description="Custom webhook URLs")
    api_keys: Dict[str, str] = Field(default_factory=dict, description="API keys for integrations")
    
    auto_backup: bool = Field(default=True, description="Enable automatic backups")
    backup_frequency: BackupFrequency = Field(default=BackupFrequency.DAILY, description="Backup frequency")
    backup_location: Optional[str] = Field(None, description="Backup storage location")
    
    custom_settings: Dict = Field(default_factory=dict, description="User-defined custom settings")

class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences."""
    user_id: str = Field(..., description="ID of the user")

class UserPreferencesUpdate(UserPreferencesBase):
    """Schema for updating user preferences."""
    pass

class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences response."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 