"""
Notification Service

This module provides notification functionality for the physical education system.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db

logger = logging.getLogger(__name__)

class Notification(BaseModel):
    """Model for notifications."""
    notification_id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    priority: str = "normal"
    created_at: datetime
    read_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationService:
    """Service for managing notifications in the physical education system."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("notification_service")
        self.db = db
        self._notifications = {}
        self._notification_counter = 0
        
    async def send_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "general",
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a notification to a user."""
        try:
            self._notification_counter += 1
            notification_id = f"notification_{self._notification_counter:06d}"
            
            notification = Notification(
                notification_id=notification_id,
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                created_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self._notifications[notification_id] = notification
            
            # Log the notification
            self.logger.info(f"Notification sent to {user_id}: {title}")
            
            return {
                "notification_id": notification_id,
                "status": "sent",
                "message": "Notification sent successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
            raise
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        try:
            user_notifications = [
                n for n in self._notifications.values()
                if n.user_id == user_id
            ]
            
            if unread_only:
                user_notifications = [
                    n for n in user_notifications
                    if n.read_at is None
                ]
            
            # Sort by created_at (newest first)
            user_notifications.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            user_notifications = user_notifications[offset:offset + limit]
            
            return [notification.dict() for notification in user_notifications]
            
        except Exception as e:
            self.logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Mark a notification as read."""
        try:
            if notification_id not in self._notifications:
                return False
            
            notification = self._notifications[notification_id]
            
            # Verify the notification belongs to the user
            if notification.user_id != user_id:
                return False
            
            notification.read_at = datetime.utcnow()
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    async def mark_all_as_read(
        self,
        user_id: str
    ) -> int:
        """Mark all notifications for a user as read."""
        try:
            count = 0
            for notification in self._notifications.values():
                if notification.user_id == user_id and notification.read_at is None:
                    notification.read_at = datetime.utcnow()
                    count += 1
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error marking all notifications as read: {str(e)}")
            return 0
    
    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Delete a notification."""
        try:
            if notification_id not in self._notifications:
                return False
            
            notification = self._notifications[notification_id]
            
            # Verify the notification belongs to the user
            if notification.user_id != user_id:
                return False
            
            del self._notifications[notification_id]
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting notification: {str(e)}")
            return False
    
    async def get_notification_stats(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get notification statistics for a user."""
        try:
            user_notifications = [
                n for n in self._notifications.values()
                if n.user_id == user_id
            ]
            
            total_notifications = len(user_notifications)
            unread_notifications = len([
                n for n in user_notifications
                if n.read_at is None
            ])
            
            # Type breakdown
            type_counts = {}
            for notification in user_notifications:
                type_counts[notification.notification_type] = type_counts.get(notification.notification_type, 0) + 1
            
            # Priority breakdown
            priority_counts = {}
            for notification in user_notifications:
                priority_counts[notification.priority] = priority_counts.get(notification.priority, 0) + 1
            
            return {
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "read_notifications": total_notifications - unread_notifications,
                "type_breakdown": type_counts,
                "priority_breakdown": priority_counts
            }
            
        except Exception as e:
            self.logger.error(f"Error getting notification stats: {str(e)}")
            return {}
    
    async def send_bulk_notification(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        notification_type: str = "general",
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send the same notification to multiple users."""
        try:
            results = []
            for user_id in user_ids:
                try:
                    result = await self.send_notification(
                        user_id=user_id,
                        title=title,
                        message=message,
                        notification_type=notification_type,
                        priority=priority,
                        metadata=metadata
                    )
                    results.append({"user_id": user_id, "status": "success", **result})
                except Exception as e:
                    results.append({"user_id": user_id, "status": "failed", "error": str(e)})
            
            success_count = len([r for r in results if r["status"] == "success"])
            failure_count = len([r for r in results if r["status"] == "failed"])
            
            return {
                "total_users": len(user_ids),
                "success_count": success_count,
                "failure_count": failure_count,
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Error sending bulk notification: {str(e)}")
            raise 