"""
Security, Access Control, and User Preferences Management Models

This module consolidates security, access control, and user preferences models from the dashboard.
It includes models for:
- Access control (roles, permissions, assignments)
- Security settings and configurations
- User preferences and settings
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin
from app.models.security.access_control.access_control_management import (
    RoleHierarchy,
    AccessControlPermission as Permission,
    AccessControlRole as Role,
    UserRole as RoleAssignment,
    RoleTemplate
)
from app.dashboard.models.user_preferences import UserPreferences

# Access Control Enums
class ResourceType(str, Enum):
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    TOOL = "tool"
    AVATAR = "avatar"
    SETTING = "setting"
    API = "api"
    SYSTEM = "system"

class ActionType(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    ADMINISTER = "administer"

class SecurityPreference(BaseModel, StatusMixin):
    """Security preferences model."""
    __tablename__ = "security_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Theme preferences
    theme = Column(String, default="light")  # light, dark, system
    accent_color = Column(String)
    font_size = Column(String, default="medium")  # small, medium, large
    font_family = Column(String, default="system")
    
    # Layout preferences
    dashboard_layout = Column(JSON)  # Custom dashboard layout
    sidebar_position = Column(String, default="left")  # left, right
    sidebar_collapsed = Column(Boolean, default=False)
    grid_view = Column(Boolean, default=True)  # grid or list view
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    in_app_notifications = Column(Boolean, default=True)
    notification_sound = Column(Boolean, default=True)
    notification_types = Column(JSON)  # Types of notifications to receive
    quiet_hours = Column(JSON)  # Time ranges for quiet hours
    
    # Language and regional preferences
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    date_format = Column(String, default="YYYY-MM-DD")
    time_format = Column(String, default="24h")  # 12h or 24h
    
    # Privacy preferences
    data_sharing = Column(Boolean, default=False)
    analytics_opt_in = Column(Boolean, default=True)
    personalized_ads = Column(Boolean, default=False)
    
    # Accessibility preferences
    high_contrast = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)
    screen_reader = Column(Boolean, default=False)
    keyboard_shortcuts = Column(JSON)  # Custom keyboard shortcuts
    
    # Performance preferences
    cache_enabled = Column(Boolean, default=True)
    cache_duration = Column(Integer, default=300)  # Cache duration in seconds
    auto_refresh = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=60)  # Refresh interval in seconds
    
    # Integration preferences
    connected_services = Column(JSON)  # List of connected third-party services
    webhook_urls = Column(JSON)  # Custom webhook URLs
    api_keys = Column(JSON)  # API keys for integrations
    
    # Backup preferences
    auto_backup = Column(Boolean, default=True)
    backup_frequency = Column(String, default="daily")  # daily, weekly, monthly
    backup_location = Column(String)  # Local or cloud storage location
    
    # Custom preferences
    custom_settings = Column(JSON)  # User-defined custom settings

    # Relationships
    user = relationship("User")

    def dict(self) -> Dict[str, Any]:
        return {
            **super().dict(),
            "user_id": self.user_id,
            "theme": self.theme,
            "accent_color": self.accent_color,
            "font_size": self.font_size,
            "font_family": self.font_family,
            "dashboard_layout": self.dashboard_layout,
            "sidebar_position": self.sidebar_position,
            "sidebar_collapsed": self.sidebar_collapsed,
            "grid_view": self.grid_view,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "in_app_notifications": self.in_app_notifications,
            "notification_sound": self.notification_sound,
            "notification_types": self.notification_types,
            "quiet_hours": self.quiet_hours,
            "language": self.language,
            "timezone": self.timezone,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "data_sharing": self.data_sharing,
            "analytics_opt_in": self.analytics_opt_in,
            "personalized_ads": self.personalized_ads,
            "high_contrast": self.high_contrast,
            "reduced_motion": self.reduced_motion,
            "screen_reader": self.screen_reader,
            "keyboard_shortcuts": self.keyboard_shortcuts,
            "cache_enabled": self.cache_enabled,
            "cache_duration": self.cache_duration,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "connected_services": self.connected_services,
            "webhook_urls": self.webhook_urls,
            "api_keys": self.api_keys,
            "auto_backup": self.auto_backup,
            "backup_frequency": self.backup_frequency,
            "backup_location": self.backup_location,
            "custom_settings": self.custom_settings
        }

class PermissionOverride(BaseModel, StatusMixin):
    """Permission override model for access control."""
    __tablename__ = "permission_overrides"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    permission_id = Column(Integer, ForeignKey("access_control_permissions.id"))
    is_allowed = Column(Boolean)
    reason = Column(String)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    permission = relationship("app.models.security.access_control.access_control_management.AccessControlPermission", back_populates="overrides")
    user = relationship("User")

    def dict(self) -> Dict[str, Any]:
        return {
            **super().dict(),
            "user_id": self.user_id,
            "permission_id": self.permission_id,
            "is_allowed": self.is_allowed,
            "reason": self.reason,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

# Re-export the classes
__all__ = ['UserPreferences', 'PermissionOverride'] 