"""
Notification Service for managing system notifications and alerts.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.gpt_models import GPTDefinition
from ..models.user import DashboardUser
from ..schemas.notification import (
    NotificationInfo,
    NotificationPreferences,
    NotificationMetrics,
    NotificationChannel
)

class NotificationService:
    """Service for managing notifications and alerts."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        severity: str = "info",
        gpt_id: Optional[str] = None,
        channel: str = "all",
        metadata: Optional[Dict[str, Any]] = None
    ) -> NotificationInfo:
        """
        Create a new notification.
        
        Args:
            user_id: The ID of the user
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            severity: Severity level (info, warning, error, critical)
            gpt_id: Optional GPT ID if notification is GPT-specific
            channel: Notification channel (email, push, in-app, all)
            metadata: Optional metadata
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            severity=severity,
            gpt_id=gpt_id,
            channel=channel,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        
        self.db.add(notification)
        self.db.commit()
        
        return NotificationInfo.from_orm(notification)
    
    async def get_user_notifications(
        self,
        user_id: str,
        time_window: str = "24h",
        include_read: bool = False,
        include_archived: bool = False,
        notification_type: Optional[str] = None,
        severity: Optional[str] = None,
        gpt_id: Optional[str] = None
    ) -> List[NotificationInfo]:
        """
        Get notifications for a user.
        
        Args:
            user_id: The ID of the user
            time_window: Time window for notifications (24h, 7d, 30d)
            include_read: Whether to include read notifications
            include_archived: Whether to include archived notifications
            notification_type: Optional notification type filter
            severity: Optional severity filter
            gpt_id: Optional GPT ID filter
        """
        # Calculate time window
        if time_window == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_window == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(days=30)
        
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.created_at >= start_time
        )
        
        if not include_read:
            query = query.filter(Notification.read_at.is_(None))
        if not include_archived:
            query = query.filter(Notification.archived_at.is_(None))
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        if severity:
            query = query.filter(Notification.severity == severity)
        if gpt_id:
            query = query.filter(Notification.gpt_id == gpt_id)
        
        notifications = query.order_by(desc(Notification.created_at)).all()
        return [NotificationInfo.from_orm(n) for n in notifications]
    
    async def mark_notification_read(
        self,
        notification_id: str,
        user_id: str
    ) -> NotificationInfo:
        """
        Mark a notification as read.
        
        Args:
            notification_id: The ID of the notification
            user_id: The ID of the user
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")
        
        notification.read_at = datetime.utcnow()
        self.db.commit()
        
        return NotificationInfo.from_orm(notification)
    
    async def archive_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> NotificationInfo:
        """
        Archive a notification.
        
        Args:
            notification_id: The ID of the notification
            user_id: The ID of the user
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise ValueError("Notification not found")
        
        notification.archived_at = datetime.utcnow()
        self.db.commit()
        
        return NotificationInfo.from_orm(notification)
    
    async def get_notification_preferences(
        self,
        user_id: str
    ) -> NotificationPreferences:
        """
        Get notification preferences for a user.
        
        Args:
            user_id: The ID of the user
        """
        user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        return NotificationPreferences(
            email_enabled=user.email_notifications,
            push_enabled=user.push_notifications,
            in_app_enabled=user.in_app_notifications,
            notification_types=user.notification_types or [],
            quiet_hours=user.quiet_hours or [],
            gpt_notifications=user.gpt_notifications or {}
        )
    
    async def update_notification_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> NotificationPreferences:
        """
        Update notification preferences for a user.
        
        Args:
            user_id: The ID of the user
            preferences: The preferences to update
        """
        user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if "email_enabled" in preferences:
            user.email_notifications = preferences["email_enabled"]
        if "push_enabled" in preferences:
            user.push_notifications = preferences["push_enabled"]
        if "in_app_enabled" in preferences:
            user.in_app_notifications = preferences["in_app_enabled"]
        if "notification_types" in preferences:
            user.notification_types = preferences["notification_types"]
        if "quiet_hours" in preferences:
            user.quiet_hours = preferences["quiet_hours"]
        if "gpt_notifications" in preferences:
            user.gpt_notifications = {
                **(user.gpt_notifications or {}),
                **preferences["gpt_notifications"]
            }
        
        self.db.commit()
        
        return await self.get_notification_preferences(user_id)
    
    async def get_notification_metrics(
        self,
        user_id: str,
        time_window: str = "24h"
    ) -> NotificationMetrics:
        """
        Get notification metrics for a user.
        
        Args:
            user_id: The ID of the user
            time_window: Time window for metrics (24h, 7d, 30d)
        """
        # Calculate time window
        if time_window == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_window == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(days=30)
        
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.created_at >= start_time
        ).all()
        
        total_notifications = len(notifications)
        read_notifications = sum(1 for n in notifications if n.read_at)
        unread_notifications = total_notifications - read_notifications
        
        notification_types = {}
        for n in notifications:
            notification_types[n.notification_type] = notification_types.get(n.notification_type, 0) + 1
        
        return NotificationMetrics(
            total_notifications=total_notifications,
            read_notifications=read_notifications,
            unread_notifications=unread_notifications,
            notification_types=notification_types,
            last_updated=datetime.utcnow()
        )
    
    async def cleanup_old_notifications(
        self,
        user_id: Optional[str] = None,
        retention_days: int = 30
    ) -> Dict[str, int]:
        """
        Clean up old notifications based on retention policy.
        
        Args:
            user_id: Optional user ID to filter notifications
            retention_days: Number of days to retain notifications
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        query = self.db.query(Notification).filter(
            Notification.created_at < cutoff_date
        )
        
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        
        deleted_count = query.delete()
        self.db.commit()
        
        return {
            "deleted_notifications": deleted_count,
            "retention_days": retention_days
        } 