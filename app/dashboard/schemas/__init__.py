"""
Dashboard Schemas Package

This package contains all the Pydantic schemas used in the dashboard application.
"""

from .dashboard_schemas import (
    DashboardPreferences,
    GPTState,
    DashboardState,
    DashboardInitResponse,
    GPTRecommendation,
    GPTSwitchResponse,
    DashboardMetrics,
    DashboardActivity,
    DashboardNotification,
    DashboardError,
    DashboardAnalytics,
    DashboardWidget
)
from .collaboration import (
    CollaborationSession,
    CollaborationDocument,
    CollaborationMetrics,
    CollaborationAnalytics,
    CollaborationWidget,
    CollaborationParticipant
)
from .context import (
    ContextHistory,
    ContextMetrics,
    ContextPatterns,
    ContextPreferences,
    ContextSharing
)
from .notification import (
    NotificationInfo,
    NotificationPreferences,
    NotificationMetrics,
    NotificationChannel
)
from .gpt import (
    GPTSubscriptionResponse,
    GPTSubscriptionCreate,
    GPTSubscriptionUpdate,
    GPTUsageStats,
    GPTSubscriptionStatus,
    GPTSubscriptionType
)

class DashboardSchemas:
    """Container class for all dashboard-related schemas."""
    # Dashboard Core Schemas
    DashboardPreferences = DashboardPreferences
    GPTState = GPTState
    DashboardState = DashboardState
    DashboardInitResponse = DashboardInitResponse
    GPTRecommendation = GPTRecommendation
    GPTSwitchResponse = GPTSwitchResponse
    DashboardMetrics = DashboardMetrics
    DashboardActivity = DashboardActivity
    DashboardNotification = DashboardNotification
    DashboardError = DashboardError
    DashboardAnalytics = DashboardAnalytics
    DashboardWidget = DashboardWidget

    # Collaboration Schemas
    CollaborationSession = CollaborationSession
    CollaborationDocument = CollaborationDocument
    CollaborationMetrics = CollaborationMetrics
    CollaborationAnalytics = CollaborationAnalytics
    CollaborationWidget = CollaborationWidget
    CollaborationParticipant = CollaborationParticipant

    # Context Schemas
    ContextHistory = ContextHistory
    ContextMetrics = ContextMetrics
    ContextPatterns = ContextPatterns
    ContextPreferences = ContextPreferences
    ContextSharing = ContextSharing

    # Notification Schemas
    NotificationInfo = NotificationInfo
    NotificationPreferences = NotificationPreferences
    NotificationMetrics = NotificationMetrics
    NotificationChannel = NotificationChannel

    # GPT Schemas
    GPTSubscriptionResponse = GPTSubscriptionResponse
    GPTSubscriptionCreate = GPTSubscriptionCreate
    GPTSubscriptionUpdate = GPTSubscriptionUpdate
    GPTUsageStats = GPTUsageStats
    GPTSubscriptionStatus = GPTSubscriptionStatus
    GPTSubscriptionType = GPTSubscriptionType

__all__ = [
    'DashboardSchemas',
    'GPTSubscriptionResponse',
    'GPTSubscriptionCreate',
    'GPTSubscriptionUpdate',
    'GPTUsageStats',
    'GPTSubscriptionStatus',
    'GPTSubscriptionType'
] 