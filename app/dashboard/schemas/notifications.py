"""
Notification Schemas

This module provides Pydantic schemas for the notification service.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class NotificationBase(BaseModel):
    """Base notification schema."""
    type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    data: Optional[Dict] = Field(None, description="Additional notification data")
    priority: str = Field("normal", description="Notification priority (low, normal, high, urgent)")

class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: str = Field(..., description="Target user ID")
    channel: str = Field("all", description="Notification channel (websocket, email, sms, all)")
    target_language: Optional[str] = Field(None, description="Target language for translation")
    source_language: Optional[str] = Field("en", description="Source language of the message")

class NotificationBroadcast(NotificationBase):
    """Schema for broadcasting a notification."""
    exclude_user: Optional[str] = Field(None, description="User ID to exclude from broadcast")

class NotificationResponse(BaseModel):
    """Response model for notification operations."""
    status: str = Field(..., description="Operation status")
    notification_id: Optional[str] = Field(None, description="Notification ID")
    delivered_at: Optional[str] = Field(None, description="Delivery timestamp")
    read_at: Optional[str] = Field(None, description="Read timestamp")
    user_id: Optional[str] = Field(None, description="User ID")
    preferences: Optional[Dict[str, bool]] = Field(None, description="User preferences")

class NotificationDetail(NotificationBase):
    """Detailed notification schema."""
    id: str = Field(..., description="Notification ID")
    status: str = Field(..., description="Notification status")
    created_at: str = Field(..., description="Creation timestamp")
    delivered_at: Optional[str] = Field(None, description="Delivery timestamp")
    read_at: Optional[str] = Field(None, description="Read timestamp")

class NotificationList(BaseModel):
    """List of notifications."""
    notifications: List[NotificationDetail] = Field(..., description="List of notifications")

class NotificationBatchingPreferences(BaseModel):
    """Smart notification batching preferences."""
    batch_enabled: bool = Field(True, description="Whether to enable smart batching")
    quiet_hours: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Quiet hours for batching (e.g. [{start: '22:00', end: '07:00'}])"
    )
    batch_interval: int = Field(
        30,
        description="Minutes to wait before sending batched notifications"
    )
    priority_threshold: str = Field(
        "normal",
        description="Minimum priority to bypass batching (urgent notifications always bypass)"
    )
    context_aware: bool = Field(
        True,
        description="Whether to use AI for context-aware batching"
    )

class SmartNotificationContext(BaseModel):
    """Context information for smart notification delivery."""
    user_timezone: str = Field(..., description="User's timezone")
    user_activity: str = Field(None, description="Current user activity/status")
    device_type: str = Field(None, description="User's current device type")
    notification_history: List[Dict] = Field(default_factory=list, description="Recent notification history")
    app_usage_patterns: Dict = Field(default_factory=dict, description="User's app usage patterns")
    environmental_context: Dict = Field(
        default_factory=dict,
        description="Environmental context (location, time, weather, etc.)"
    )

class NotificationAccessibility(BaseModel):
    """Accessibility preferences for notifications."""
    text_to_speech: bool = Field(False, description="Enable text-to-speech for notifications")
    high_contrast: bool = Field(False, description="Use high contrast for visual notifications")
    font_size: str = Field("normal", description="Preferred font size (small, normal, large, x-large)")
    screen_reader_optimized: bool = Field(False, description="Optimize content for screen readers")
    vibration_pattern: str = Field("standard", description="Custom vibration pattern for mobile")
    color_blind_mode: str = Field(None, description="Color blind mode preference")

class NotificationInteractivity(BaseModel):
    """Interactive notification features."""
    quick_actions: List[str] = Field(default_factory=list, description="Enabled quick actions")
    voice_commands: bool = Field(False, description="Enable voice command responses")
    gesture_control: bool = Field(False, description="Enable gesture controls for notifications")
    smart_suggestions: bool = Field(True, description="Enable AI-powered response suggestions")
    contextual_reminders: bool = Field(True, description="Enable context-based reminders")

class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""
    preferences: Dict[str, bool] = Field(
        ...,
        description="Notification preferences by type",
        example={
            "system": True,
            "resource": True,
            "security": True,
            "optimization": True,
            "collaboration": True,
            "achievement": True
        }
    )
    batching: Optional[NotificationBatchingPreferences] = Field(None, description="Batching preferences")
    smart_context: Optional[SmartNotificationContext] = Field(None, description="Smart delivery context")
    accessibility: Optional[NotificationAccessibility] = Field(None, description="Accessibility preferences")
    interactivity: Optional[NotificationInteractivity] = Field(None, description="Interactive features")
    language_preferences: Dict[str, str] = Field(
        default_factory=dict,
        description="Language preferences by notification type"
    )

class SystemNotificationData(BaseModel):
    """System notification data."""
    component: str = Field(..., description="System component")
    action: str = Field(..., description="System action")
    details: Optional[Dict] = Field(None, description="Additional details")

class ResourceNotificationData(BaseModel):
    """Resource notification data."""
    resource_id: str = Field(..., description="Resource ID")
    resource_type: str = Field(..., description="Resource type")
    action: str = Field(..., description="Resource action")
    metrics: Optional[Dict] = Field(None, description="Resource metrics")

class SecurityNotificationData(BaseModel):
    """Security notification data."""
    alert_type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    details: str = Field(..., description="Alert details")
    recommendations: Optional[List[str]] = Field(None, description="Security recommendations")

class OptimizationNotificationData(BaseModel):
    """Optimization notification data."""
    metric: str = Field(..., description="Optimization metric")
    current_value: float = Field(..., description="Current metric value")
    threshold: float = Field(..., description="Metric threshold")
    recommendations: Optional[List[str]] = Field(None, description="Optimization recommendations")

class CollaborationNotificationData(BaseModel):
    """Collaboration notification data."""
    action: str = Field(..., description="Collaboration action")
    user: Dict = Field(..., description="User information")
    resource: Dict = Field(..., description="Resource information")
    details: Optional[Dict] = Field(None, description="Additional details")

class AchievementNotificationData(BaseModel):
    """Achievement notification data."""
    achievement_type: str = Field(..., description="Achievement type")
    level: str = Field(..., description="Achievement level")
    description: str = Field(..., description="Achievement description")
    rewards: Optional[List[Dict]] = Field(None, description="Achievement rewards") 