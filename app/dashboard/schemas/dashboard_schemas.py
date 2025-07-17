"""
Dashboard Schemas

This module defines the Pydantic schemas for the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from .collaboration import (
    CollaborationSession,
    CollaborationDocument,
    CollaborationMetrics,
    CollaborationAnalytics,
    CollaborationWidget,
    CollaborationParticipant
)

class DashboardPreferences(BaseModel):
    """User dashboard preferences."""
    theme: Optional[str] = None
    layout: Optional[Dict] = None
    widgets: Optional[List[Dict]] = None
    filters: Optional[List[Dict]] = None
    notifications: Optional[Dict] = None

class GPTState(BaseModel):
    """Schema for GPT state in dashboard."""
    gpt_id: str
    status: str
    is_primary: bool
    performance: Optional[Dict] = None

class DashboardState(BaseModel):
    """Current dashboard state."""
    active_contexts: Optional[List[Dict]] = None
    metrics: Optional[Dict] = None
    analytics: Optional[Dict] = None
    performance: Optional[Dict] = None
    collaboration: Optional[Dict] = None

class DashboardInitResponse(BaseModel):
    """Dashboard initialization response."""
    preferences: DashboardPreferences
    metrics: Optional[Dict] = None
    analytics: Optional[Dict] = None
    performance: Optional[Dict] = None

class GPTRecommendation(BaseModel):
    """GPT recommendation data."""
    gpt_id: str
    name: str
    score: float
    metrics: Optional[Dict] = None
    analytics: Optional[Dict] = None
    performance: Optional[Dict] = None

class GPTSwitchResponse(BaseModel):
    """GPT switch response data."""
    success: bool
    gpt_id: str
    validation: Optional[Dict] = None
    impact: Optional[Dict] = None
    metrics: Optional[Dict] = None

class DashboardMetrics(BaseModel):
    """Dashboard metrics data."""
    performance_metrics: Optional[Dict] = None
    usage_metrics: Optional[Dict] = None
    health_metrics: Optional[Dict] = None
    collaboration_metrics: Optional[Dict] = None

class DashboardAnalytics(BaseModel):
    """Dashboard analytics data."""
    trends: Optional[Dict] = None
    patterns: Optional[Dict] = None
    forecasts: Optional[Dict] = None
    collaboration_analytics: Optional[Dict] = None

class DashboardPerformance(BaseModel):
    """Dashboard performance data."""
    benchmarks: Optional[Dict] = None
    optimization: Optional[Dict] = None
    recommendations: Optional[Dict] = None

class DashboardIntegration(BaseModel):
    """Dashboard integration data."""
    status: Optional[Dict] = None
    metrics: Optional[Dict] = None
    recommendations: Optional[Dict] = None

class DashboardWidget(BaseModel):
    """Dashboard widget data."""
    id: str
    type: str
    data: Optional[Dict] = None
    config: Optional[Dict] = None
    position: Optional[Dict] = None
    size: Optional[Dict] = None

class DashboardActivity(BaseModel):
    """Schema for dashboard activity."""
    activity_id: str
    activity_type: str
    timestamp: datetime
    details: Dict
    user_id: str
    related_gpts: List[str]
    context_id: Optional[str] = None

    class Config:
        from_attributes = True

class DashboardNotification(BaseModel):
    """Schema for dashboard notifications."""
    notification_id: str
    type: str
    title: str
    message: str
    timestamp: datetime
    is_read: bool
    priority: str
    metadata: Optional[Dict] = None

    class Config:
        from_attributes = True

class DashboardError(BaseModel):
    """Schema for dashboard errors."""
    error_code: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime
    context: Optional[Dict] = None

    model_config = ConfigDict(from_attributes=True)

class DashboardAnalytics(BaseModel):
    """Schema for dashboard analytics."""
    usage_trends: List[int]
    peak_hours: List[str]
    popular_features: List[str]
    user_engagement: Dict[str, float]
    collaboration_analytics: Optional[CollaborationAnalytics] = None
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "usage_trends": [100, 120, 150],
                "peak_hours": ["10:00", "14:00", "16:00"],
                "popular_features": ["chat", "document_sharing", "video_calls"],
                "user_engagement": {
                    "daily": 0.8,
                    "weekly": 0.6,
                    "monthly": 0.4
                },
                "collaboration_analytics": {
                    "summary": {
                        "total_collaborations": 100,
                        "active_users": 50,
                        "engagement_rate": 0.85
                    },
                    "trends": {
                        "daily_active_users": [45, 48, 50],
                        "document_edits": [120, 150, 180]
                    }
                },
                "last_updated": "2024-05-01T00:00:00Z"
            }
        }

class DashboardWidget(BaseModel):
    """Schema for dashboard widgets."""
    id: str
    widget_type: str
    title: str
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    collaboration_widget: Optional[CollaborationWidget] = None
    position: Dict[str, int]
    size: Dict[str, int]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "widget-123",
                "widget_type": "metrics",
                "title": "System Metrics",
                "description": "Shows key system metrics",
                "data": {
                    "active_users": 500,
                    "response_time": 200
                },
                "config": {
                    "refresh_interval": 30,
                    "chart_type": "line"
                },
                "collaboration_widget": {
                    "id": "collab-widget-1",
                    "widget_type": "active_sessions",
                    "title": "Active Sessions",
                    "data": {
                        "sessions": [
                            {"id": "session-1", "participants": 5}
                        ]
                    }
                },
                "position": {"x": 0, "y": 0},
                "size": {"width": 2, "height": 2},
                "created_at": "2024-05-01T00:00:00Z",
                "updated_at": "2024-05-01T00:00:00Z"
            }
        } 