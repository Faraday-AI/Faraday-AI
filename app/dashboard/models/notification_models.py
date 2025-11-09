"""
Dashboard Notification Models

This module defines the database models for the dashboard notification system.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class NotificationChannel(str, enum.Enum):
    """Available notification channels."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WEBSOCKET = "websocket"
    IN_APP = "in_app"

class NotificationPriority(str, enum.Enum):
    """Notification priority levels."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class NotificationType(str, enum.Enum):
    """Types of notifications."""
    SYSTEM = "system"
    ALERT = "alert"
    UPDATE = "update"
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"

class Notification(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing dashboard notifications."""
    __tablename__ = "dashboard_notification_models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType, name='dashboard_notification_type_enum'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    data = Column(JSON)
    priority = Column(Enum(NotificationPriority, name='dashboard_notification_priority_enum'), default=NotificationPriority.NORMAL)
    status = Column(String, default="unread")
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="dashboard_notifications")
    channels = relationship("DashboardNotificationChannel", back_populates="notification")

# Store enum reference for NotificationPreference before model class overwrites it
_NotificationChannelEnumForPref = NotificationChannel

class NotificationPreference(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing dashboard notification preferences."""
    __tablename__ = "dashboard_notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(Enum(_NotificationChannelEnumForPref, name='notification_channel_enum'), nullable=False)
    type = Column(Enum(NotificationType, name='dashboard_notification_type_enum'), nullable=False)
    enabled = Column(Boolean, default=True)
    priority_threshold = Column(Enum(NotificationPriority, name='dashboard_notification_priority_enum'), default=NotificationPriority.LOW)
    quiet_hours_start = Column(String)
    quiet_hours_end = Column(String)
    timezone = Column(String, default="UTC")
    batching_enabled = Column(Boolean, default=False)
    batching_interval = Column(Integer, default=5)  # minutes

    # Relationships
    user = relationship("User", back_populates="dashboard_notification_preferences")

# Store enum reference before model class overwrites it
_NotificationChannelEnum = NotificationChannel

class DashboardNotificationChannel(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing notification channel configurations."""
    __tablename__ = "dashboard_notification_channels"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("dashboard_notification_models.id"), nullable=False)
    channel = Column(Enum(_NotificationChannelEnum, name='notification_channel_enum'), nullable=False)
    status = Column(String, default="pending")
    sent_at = Column(DateTime)
    error = Column(String)
    retry_count = Column(Integer, default=0)
    last_retry = Column(DateTime)

    # Relationships
    notification = relationship("Notification", back_populates="channels") 