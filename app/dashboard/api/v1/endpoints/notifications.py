"""
Notification API endpoints for the Faraday AI Dashboard.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket
from sqlalchemy.orm import Session

from app.dashboard.services.notification_service import NotificationService
from app.dashboard.schemas.notification import (
    NotificationInfo,
    NotificationPreferences,
    NotificationMetrics,
    NotificationChannel,
    NotificationResponse,
    NotificationCreate,
    NotificationBroadcast,
    NotificationList,
    NotificationPreferenceUpdate
)
from app.dashboard.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("/notifications", response_model=List[NotificationInfo])
async def get_notifications(
    time_window: Optional[int] = Query(7, description="Time window in days"),
    include_read: bool = Query(False, description="Include read notifications"),
    include_archived: bool = Query(False, description="Include archived notifications"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    gpt_id: Optional[str] = Query(None, description="Filter by GPT ID"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get notifications for the current user."""
    service = NotificationService(db)
    return service.get_user_notifications(
        user_id=current_user["id"],
        time_window=time_window,
        include_read=include_read,
        include_archived=include_archived,
        notification_type=notification_type,
        severity=severity,
        gpt_id=gpt_id
    )

@router.post("/notifications", response_model=NotificationInfo)
async def create_notification(
    title: str,
    message: str,
    notification_type: str,
    severity: str = "info",
    gpt_id: Optional[str] = None,
    channel: str = "all",
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new notification."""
    service = NotificationService(db)
    return service.create_notification(
        user_id=current_user["id"],
        title=title,
        message=message,
        notification_type=notification_type,
        severity=severity,
        gpt_id=gpt_id,
        channel=channel,
        metadata=metadata or {}
    )

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a notification as read."""
    service = NotificationService(db)
    service.mark_notification_read(notification_id, current_user["id"])
    return {"status": "success"}

@router.put("/notifications/{notification_id}/archive")
async def archive_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Archive a notification."""
    service = NotificationService(db)
    service.archive_notification(notification_id, current_user["id"])
    return {"status": "success"}

@router.get("/preferences", response_model=NotificationPreferences)
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get notification preferences for the current user."""
    service = NotificationService(db)
    return service.get_notification_preferences(current_user["id"])

@router.put("/preferences", response_model=NotificationPreferences)
async def update_preferences(
    preferences: NotificationPreferences,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update notification preferences for the current user."""
    service = NotificationService(db)
    return service.update_notification_preferences(current_user["id"], preferences)

@router.get("/metrics", response_model=NotificationMetrics)
async def get_metrics(
    time_window: Optional[int] = Query(30, description="Time window in days"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get notification metrics for the current user."""
    service = NotificationService(db)
    return service.get_notification_metrics(current_user["id"], time_window)

@router.get("/channels", response_model=List[NotificationChannel])
async def get_channels(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get notification channels for the current user."""
    service = NotificationService(db)
    return service.get_notification_channels(current_user["id"])

@router.put("/channels/{channel_type}", response_model=NotificationChannel)
async def update_channel(
    channel_type: str,
    channel: NotificationChannel,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update notification channel settings for the current user."""
    service = NotificationService(db)
    return service.update_notification_channel(current_user["id"], channel_type, channel)

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications."""
    notification_service = RealTimeNotificationService(db)
    await notification_service.connection_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming WebSocket messages if needed
            await websocket.send_json({"status": "received", "data": data})
    except Exception as e:
        await notification_service.connection_manager.disconnect(websocket, user_id)

@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Send a notification to a user.
    
    Args:
        notification: Notification details
    """
    try:
        service = RealTimeNotificationService(db)
        result = await service.send_notification(
            user_id=notification.user_id,
            notification_type=notification.type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            priority=notification.priority,
            channel=notification.channel
        )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {str(e)}"
        )

@router.post("/broadcast", response_model=NotificationResponse)
async def broadcast_notification(
    notification: NotificationBroadcast,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Broadcast a notification to all users.
    
    Args:
        notification: Notification details
    """
    try:
        service = RealTimeNotificationService(db)
        result = await service.broadcast_notification(
            notification_type=notification.type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            priority=notification.priority,
            exclude_user=notification.exclude_user
        )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error broadcasting notification: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=NotificationList)
async def get_user_notifications(
    user_id: str,
    notification_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, gt=0, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get notifications for a user.
    
    Args:
        user_id: User ID
        notification_type: Optional notification type filter
        status: Optional status filter
        limit: Maximum number of notifications to return
        offset: Number of notifications to skip
    """
    try:
        service = RealTimeNotificationService(db)
        notifications = await service.get_user_notifications(
            user_id=user_id,
            notification_type=notification_type,
            status=status,
            limit=limit,
            offset=offset
        )
        return {"notifications": notifications}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting notifications: {str(e)}"
        )

@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a notification as read.
    
    Args:
        notification_id: Notification ID
    """
    try:
        service = RealTimeNotificationService(db)
        result = await service.mark_notification_read(
            user_id=current_user["id"],
            notification_id=notification_id
        )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error marking notification as read: {str(e)}"
        )

@router.put("/preferences", response_model=NotificationResponse)
async def update_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update notification preferences.
    
    Args:
        preferences: Updated notification preferences
    """
    try:
        service = RealTimeNotificationService(db)
        result = await service.update_notification_preferences(
            user_id=current_user["id"],
            preferences=preferences.preferences
        )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating notification preferences: {str(e)}"
        ) 