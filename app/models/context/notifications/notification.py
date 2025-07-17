"""
Notification Models

This module defines the database models for user notifications and preferences
in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.shared_base import SharedBase
from app.models.mixins import StatusMixin, MetadataMixin

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
    RESOURCE = "resource"
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    COLLABORATION = "collaboration"
    ACHIEVEMENT = "achievement"

class Notification(SharedBase, StatusMixin, MetadataMixin):
    """Model for storing notifications."""
    __tablename__ = "context_notifications"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType, name='notification_type_enum'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    data = Column(JSON)
    priority = Column(Enum(NotificationPriority, name='notification_priority_enum'), default=NotificationPriority.NORMAL)
    read_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="notifications")
    channels = relationship("NotificationChannel", back_populates="notification")

class NotificationPreference(SharedBase, StatusMixin, MetadataMixin):
    """Model for storing user notification preferences."""
    __tablename__ = "context_notification_preferences"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(Enum(NotificationChannel, name='notification_channel_enum'), nullable=False)
    type = Column(Enum(NotificationType, name='notification_type_enum'), nullable=False)
    priority_threshold = Column(Enum(NotificationPriority, name='notification_priority_enum'), default=NotificationPriority.LOW)
    quiet_hours_start = Column(String)
    quiet_hours_end = Column(String)
    timezone = Column(String, default="UTC")
    batching_enabled = Column(Boolean, default=False)
    batching_interval = Column(Integer, default=5)  # minutes

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

class NotificationChannel(SharedBase, StatusMixin, MetadataMixin):
    """Model for storing notification channel configurations."""
    __tablename__ = "context_notification_channels"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    channel = Column(Enum(NotificationChannel, name='notification_channel_enum'), nullable=False)
    sent_at = Column(DateTime)
    error = Column(String)
    retry_count = Column(Integer, default=0)
    last_retry = Column(DateTime)

    # Relationships
    notification = relationship("Notification", back_populates="channels") 