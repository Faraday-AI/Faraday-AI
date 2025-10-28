"""
Resource and Notification Management Models

This module defines the database models for resource management,
monitoring, optimization, and notification handling in the Faraday AI application.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin, AuditableModel
from app.models.physical_education.base.base_class import Base

# Resource Management Enums
class ResourceType(str, enum.Enum):
    """Types of resources that can be monitored."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"

class ResourceMetric(str, enum.Enum):
    """Types of metrics that can be collected."""
    USAGE = "usage"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    COST = "cost"
    EFFICIENCY = "efficiency"

class ThresholdType(str, enum.Enum):
    """Types of resource thresholds."""
    WARNING = "warning"
    CRITICAL = "critical"

class OptimizationStatus(str, enum.Enum):
    """Status of optimization recommendations."""
    PENDING = "pending"
    APPLIED = "applied"
    REJECTED = "rejected"
    FAILED = "failed"

class SharingType(str, enum.Enum):
    """Types of resource sharing."""
    USER = "user"
    PROJECT = "project"
    ORGANIZATION = "organization"

class SharingScope(str, enum.Enum):
    """Scopes of resource sharing."""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"

# Notification Management Enums
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

# Resource Management Models
class ResourceUsage(BaseModel, MetadataMixin):
    """Model for storing resource usage metrics."""
    __tablename__ = "resource_management_notification_usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    usage_type = Column(String, nullable=False)
    usage_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resource_usage")
    # organization = relationship("Organization", back_populates="resource_usage")
    # resource = relationship("Resource", back_populates="usage")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "resource_id": self.resource_id,
            "usage_type": self.usage_type,
            "usage_data": self.usage_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ResourceNotificationThreshold(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource notification thresholds."""
    __tablename__ = "resource_notification_thresholds"

    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    threshold_value = Column(Float, nullable=False)
    threshold_type = Column(Enum(ThresholdType, name='threshold_type_enum'), nullable=False)
    action = Column(String, nullable=False)  # 'notify', 'scale', 'alert', etc.
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    user = relationship("User", back_populates="resource_thresholds")
    project = relationship("DashboardProject", back_populates="resource_thresholds")
    organization = relationship("Organization", back_populates="resource_thresholds")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "resource_type": self.resource_type.value if self.resource_type else None,
            "metric_type": self.metric_type.value if self.metric_type else None,
            "threshold_value": self.threshold_value,
            "threshold_type": self.threshold_type.value if self.threshold_type else None,
            "action": self.action,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        }

class ResourceNotificationOptimization(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource notification optimization recommendations."""
    __tablename__ = "resource_notification_optimizations"

    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    current_value = Column(Float, nullable=False)
    recommended_value = Column(Float, nullable=False)
    potential_savings = Column(Float)
    confidence_score = Column(Float)
    recommendation = Column(String, nullable=False)
    status = Column(Enum(OptimizationStatus, name='optimization_status_enum'), default=OptimizationStatus.PENDING)
    applied_at = Column(DateTime)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    user = relationship("User", back_populates="resource_optimizations")
    project = relationship("DashboardProject", back_populates="resource_optimizations")
    organization = relationship("Organization", back_populates="resource_optimizations")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "resource_type": self.resource_type.value if self.resource_type else None,
            "metric_type": self.metric_type.value if self.metric_type else None,
            "current_value": self.current_value,
            "recommended_value": self.recommended_value,
            "potential_savings": self.potential_savings,
            "confidence_score": self.confidence_score,
            "recommendation": self.recommendation,
            "status": self.status.value if self.status else None,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        }

class ResourceSharing(BaseModel, StatusMixin, MetadataMixin):
    """Model for managing resource sharing between users and projects."""
    __tablename__ = "resource_management_notification_sharing"

    resource_id = Column(Integer, primary_key=True)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    is_shared = Column(Boolean, default=False)
    sharing_type = Column(Enum(SharingType, name='sharing_type_enum'), nullable=False)
    sharing_permissions = Column(JSON, nullable=False)
    sharing_scope = Column(Enum(SharingScope, name='sharing_scope_enum'), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_with_project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    shared_with_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_resources")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id], back_populates="shared_resources")
    shared_with_project = relationship("DashboardProject", back_populates="shared_resources")
    shared_with_organization = relationship("Organization", back_populates="shared_resources")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value if self.resource_type else None,
            "is_shared": self.is_shared,
            "sharing_type": self.sharing_type.value if self.sharing_type else None,
            "sharing_permissions": self.sharing_permissions,
            "sharing_scope": self.sharing_scope.value if self.sharing_scope else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "owner_id": self.owner_id,
            "shared_with_user_id": self.shared_with_user_id,
            "shared_with_project_id": self.shared_with_project_id,
            "shared_with_organization_id": self.shared_with_organization_id
        }

class ResourceNotificationEvent(BaseModel, StatusMixin, MetadataMixin):
    """Model for tracking resource notification events and their status."""
    __tablename__ = "resource_notification_events"

    event_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # 'info', 'warning', 'critical'
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    description = Column(String, nullable=False)
    action_taken = Column(String, nullable=True)
    action_result = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Relationships
    user = relationship("User", back_populates="optimization_events")
    project = relationship("DashboardProject", back_populates="optimization_events")
    organization = relationship("Organization", back_populates="optimization_events")
    resource = relationship("Resource", back_populates="optimization_events")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "event_type": self.event_type,
            "severity": self.severity,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value if self.resource_type else None,
            "metric_type": self.metric_type.value if self.metric_type else None,
            "description": self.description,
            "action_taken": self.action_taken,
            "action_result": self.action_result,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        }

# Notification Management Models
class Notification(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing notifications."""
    __tablename__ = "resource_management_notifications"

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

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value if self.type else None,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "priority": self.priority.value if self.priority else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

class NotificationPreference(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing user notification preferences."""
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(Enum(NotificationChannel, name='notification_channel_enum'), nullable=False)
    type = Column(Enum(NotificationType, name='notification_type_enum'), nullable=False)
    enabled = Column(Boolean, default=True)
    priority_threshold = Column(Enum(NotificationPriority, name='notification_priority_enum'), default=NotificationPriority.LOW)
    quiet_hours_start = Column(String)
    quiet_hours_end = Column(String)
    timezone = Column(String, default="UTC")
    batching_enabled = Column(Boolean, default=False)
    batching_interval = Column(Integer, default=5)  # minutes

    # Relationships
    user = relationship("User", back_populates="notification_preferences")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel.value if self.channel else None,
            "type": self.type.value if self.type else None,
            "enabled": self.enabled,
            "priority_threshold": self.priority_threshold.value if self.priority_threshold else None,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "timezone": self.timezone,
            "batching_enabled": self.batching_enabled,
            "batching_interval": self.batching_interval
        }

class NotificationChannel(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing notification channel configurations."""
    __tablename__ = "resource_management_notification_channels"

    id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    channel = Column(Enum(NotificationChannel, name='notification_channel_enum'), nullable=False)
    sent_at = Column(DateTime)
    error = Column(String)
    retry_count = Column(Integer, default=0)
    last_retry = Column(DateTime)

    # Relationships
    notification = relationship("Notification", back_populates="channels")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "notification_id": self.notification_id,
            "channel": self.channel.value if self.channel else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error": self.error,
            "retry_count": self.retry_count,
            "last_retry": self.last_retry.isoformat() if self.last_retry else None
        }

class ResourceNotificationType(str, enum.Enum):
    """Types of resource notifications."""
    ALLOCATION = "allocation"
    DEALLOCATION = "deallocation"
    MAINTENANCE = "maintenance"
    UPGRADE = "upgrade"
    ISSUE = "issue"
    RESOLUTION = "resolution"

class ResourceNotificationPriority(str, enum.Enum):
    """Resource notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ResourceNotification(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource-related notifications."""
    __tablename__ = "resource_notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    notification_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resource_notifications")
    organization = relationship("Organization", back_populates="resource_notifications")
    resource = relationship("Resource", back_populates="notifications")

class ResourceNotificationPreference(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource notification preferences."""
    __tablename__ = "resource_notification_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_type = Column(String, nullable=False)
    type = Column(Enum(ResourceNotificationType, name='resource_notification_type_enum'), nullable=False)
    priority_threshold = Column(Enum(ResourceNotificationPriority, name='resource_notification_priority_enum'), default=ResourceNotificationPriority.LOW)
    quiet_hours_start = Column(String)
    quiet_hours_end = Column(String)
    timezone = Column(String, default="UTC")
    batching_enabled = Column(Boolean, default=False)
    batching_interval = Column(Integer, default=5)  # minutes

    # Relationships
    user = relationship("User", back_populates="resource_notification_preferences")

class ResourceShare(BaseModel, StatusMixin, MetadataMixin):
    """Model for resource sharing."""
    __tablename__ = "resource_shares"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    shared_with_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    permissions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="resource_shares")
    organization = relationship("Organization", foreign_keys=[organization_id], back_populates="resource_shares")
    shared_with_organization = relationship("Organization", foreign_keys=[shared_with_organization_id], back_populates="shared_resource_shares")
    resource = relationship("Resource", back_populates="shares")

class ResourceAnalytics(BaseModel, StatusMixin, MetadataMixin):
    """Model for resource analytics."""
    __tablename__ = "resource_analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resource_analytics")
    organization = relationship("Organization", back_populates="resource_analytics")
    resource = relationship("Resource", back_populates="analytics")

class ResourceFeedback(BaseModel, StatusMixin, MetadataMixin):
    """Model for resource feedback."""
    __tablename__ = "resource_feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resource_feedback")
    organization = relationship("Organization", back_populates="resource_feedback")
    resource = relationship("Resource", back_populates="feedback") 