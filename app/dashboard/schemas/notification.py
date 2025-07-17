"""
Notification schemas for the Faraday AI Dashboard.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

class NotificationInfo(BaseModel):
    """Schema for notification information."""
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    severity: str = Field(default="info", pattern="^(info|warning|error|critical)$")
    gpt_id: Optional[str] = None
    channel: str = Field(default="all", pattern="^(email|push|in-app|all)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    read_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationPreferences(BaseModel):
    """Schema for notification preferences."""
    email_enabled: bool = Field(default=True)
    push_enabled: bool = Field(default=True)
    in_app_enabled: bool = Field(default=True)
    notification_types: List[str] = Field(default_factory=list)
    quiet_hours: List[Dict[str, int]] = Field(default_factory=list)
    gpt_notifications: Dict[str, Dict[str, bool]] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class NotificationMetrics(BaseModel):
    """Schema for notification metrics."""
    total_notifications: int
    read_notifications: int
    unread_notifications: int
    notification_types: Dict[str, int]
    last_updated: datetime

    class Config:
        from_attributes = True

class NotificationChannel(BaseModel):
    """Schema for notification channel configuration."""
    channel_type: str = Field(pattern="^(email|push|in-app)$")
    enabled: bool = Field(default=True)
    settings: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    user_id: str
    type: str = Field(pattern="^(info|warning|error|critical)$")
    title: str
    message: str
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    channel: str = Field(default="all", pattern="^(email|push|in-app|all)$")

    class Config:
        from_attributes = True

class NotificationBroadcast(BaseModel):
    """Schema for broadcasting a notification."""
    type: str = Field(pattern="^(info|warning|error|critical)$")
    title: str
    message: str
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    exclude_user: Optional[str] = None

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    """Schema for notification response."""
    status: str
    message: str
    notification_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class NotificationList(BaseModel):
    """Schema for list of notifications."""
    notifications: List[NotificationInfo]

    class Config:
        from_attributes = True

class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""
    preferences: Dict[str, Any]

    class Config:
        from_attributes = True 