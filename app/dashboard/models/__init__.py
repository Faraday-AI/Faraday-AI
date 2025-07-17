"""
Dashboard Models Package

This package contains all the database models used in the dashboard application.
"""

# Import specific models that are referenced directly
from .user_preferences import UserPreferences
from .tool_registry import Tool, UserTool
from .access_control import (
    Permission,
    Role,
    RoleAssignment,
    RoleHierarchy,
    RoleTemplate
)
from app.models.security.preferences.security_preferences_management import PermissionOverride
from .context import (
    GPTContext,
    ContextInteraction,
    SharedContext,
    ContextSummary,
    ContextTemplate,
    ContextBackup,
    ContextMetrics,
    ContextValidation,
    ContextOptimization
)
from .gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTUsage,
    GPTIntegration,
    GPTAnalytics,
    GPTFeedback,
    GPTPerformance,
    GPTUsageHistory
)
from .feedback import Feedback
from .project import DashboardProject
from .organization_models import Organization
from app.models.organization.base.organization_management import Department  # Import Department from correct module
from .team import DashboardTeam, DashboardTeamMember
from .notification_models import (
    Notification,
    NotificationPreference,
    NotificationChannel,
    NotificationType,
    NotificationPriority
)
from .resource_models import (
    DashboardResourceUsage,
    DashboardResourceThreshold,
    DashboardResourceOptimization,
    ResourceType,
    ResourceMetric,
    DashboardResourceSharing,
    DashboardOptimizationEvent
)
from .dashboard_models import (
    Dashboard,
    DashboardWidget,
    WidgetType,
    WidgetLayout,
    DashboardShare,
    DashboardFilter,
    DashboardAnalytics
)
from .user import DashboardUser  # Import directly from user module
from .security import (
    DashboardAPIKey,
    DashboardRateLimit,
    IPAllowlist,
    IPBlocklist,
    AuditLog,
    SecurityPolicy,
    Session,
    APIKeyInfo,
    RoleInfo,
    SecurityMetrics
)
from .ai_tool import AITool  # Import AITool from its own module
from .category import Category  # Import Category from its own module
from .gpt_version import GPTVersion  # Import GPTVersion from its own module
from .webhook import Webhook  # Import Webhook from its own module
from .comment import Comment  # Import Comment from its own module
from .ai_suite import AISuite  # Import AISuite from its own module
from .marketplace_listing import MarketplaceListing  # Import MarketplaceListing from its own module
from .tool_usage_log import ToolUsageLog  # Import ToolUsageLog from its own module

# Create User alias for DashboardUser
User = DashboardUser

# Define DashboardModels class directly here instead of importing it
class DashboardModels:
    """Container class for all dashboard-related models."""
    Dashboard = Dashboard
    DashboardWidget = DashboardWidget
    WidgetType = WidgetType
    WidgetLayout = WidgetLayout
    DashboardShare = DashboardShare
    DashboardFilter = DashboardFilter
    DashboardAnalytics = DashboardAnalytics
    Category = Category
    GPTVersion = GPTVersion
    Webhook = Webhook
    DashboardTeam = DashboardTeam
    DashboardTeamMember = DashboardTeamMember
    Comment = Comment
    AISuite = AISuite
    MarketplaceListing = MarketplaceListing
    ToolUsageLog = ToolUsageLog
    Department = Department  # Add Department to DashboardModels

__all__ = [
    'User',  # Add User alias
    'UserPreferences',
    'Tool',
    'UserTool',
    'Permission',
    'Role',
    'RoleAssignment',
    'PermissionOverride',
    'RoleHierarchy',
    'RoleTemplate',
    'GPTDefinition',
    'DashboardGPTSubscription',
    'GPTUsage',
    'GPTIntegration',
    'GPTAnalytics',
    'GPTFeedback',
    'GPTPerformance',
    'GPTUsageHistory',
    'GPTContext',
    'ContextInteraction',
    'SharedContext',
    'ContextSummary',
    'ContextTemplate',
    'ContextBackup',
    'ContextMetrics',
    'ContextValidation',
    'ContextOptimization',
    'Feedback',
    'Project',
    'Organization',
    'Department',  # Add Department to __all__
    'DashboardTeam',
    'DashboardTeamMember',
    'Notification',
    'NotificationPreference',
    'NotificationChannel',
    'NotificationType',
    'NotificationPriority',
    'DashboardResourceUsage',
    'DashboardResourceThreshold',
    'DashboardResourceOptimization',
    'ResourceType',
    'ResourceMetric',
    'DashboardResourceSharing',
    'DashboardOptimizationEvent',
    'Dashboard',
    'DashboardWidget',
    'WidgetType',
    'WidgetLayout',
    'DashboardShare',
    'DashboardFilter',
    'DashboardAnalytics',
    'DashboardModels',
    'DashboardUser',
    'AITool',
    'Category',
    'GPTVersion',  # Add GPTVersion to __all__
    'Webhook',  # Add Webhook to __all__
    'Comment',  # Add Comment to __all__
    'AISuite',  # Add AISuite to __all__
    'MarketplaceListing',  # Add MarketplaceListing to __all__
    'ToolUsageLog',  # Add ToolUsageLog to __all__
    # Add security models
    'DashboardAPIKey',
    'DashboardRateLimit',
    'IPAllowlist',
    'IPBlocklist',
    'AuditLog',
    'SecurityPolicy',
    'Session',
    'APIKeyInfo',
    'RoleInfo',
    'SecurityMetrics'
] 