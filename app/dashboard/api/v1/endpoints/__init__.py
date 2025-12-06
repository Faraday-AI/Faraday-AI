"""API endpoints for the dashboard."""

from fastapi import APIRouter

api_router = APIRouter()

# Import routers directly from their modules
from .access_control import router as access_control_router
from .ai_widgets import router as ai_widgets_router
from .analytics import router as analytics_router
from .avatars import router as avatars_router
from .collaboration import router as collaboration_router
from .compatibility import router as compatibility_router
from .dashboard import router as dashboard_router
from .gpt_context import router as gpt_context_router
from .gpt_coordination import router as gpt_coordination_router
from .gpt_function import router as gpt_function_router
from .gpt_manager import router as gpt_manager_router
from .monitoring import router as monitoring_router
from .notifications import router as notifications_router
from .optimization_monitoring import router as optimization_monitoring_router
from .organization import router as organization_router
from .organization_analytics import router as organization_analytics_router
from .recommendations import router as recommendations_router
from .resource_optimization import router as resource_optimization_router
from .resource_sharing import router as resource_sharing_router
from .security import router as security_router
from .tool_registry import router as tool_registry_router
from .user_preferences import router as user_preferences_router
from .widget_export import router as widget_export_router

# Include routers with their prefixes
api_router.include_router(access_control_router, prefix="/access-control", tags=["access-control"])
api_router.include_router(ai_widgets_router, prefix="/ai-widgets", tags=["ai-widgets"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(avatars_router, prefix="/avatars", tags=["avatars"])
api_router.include_router(collaboration_router, prefix="/collaboration", tags=["collaboration"])
api_router.include_router(compatibility_router, prefix="/compatibility", tags=["compatibility"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(gpt_context_router, prefix="/gpt/context", tags=["gpt"])
api_router.include_router(gpt_coordination_router, prefix="/gpt/coordination", tags=["gpt"])
api_router.include_router(gpt_function_router, prefix="/gpt/functions", tags=["gpt"])
api_router.include_router(gpt_manager_router, prefix="/gpt/manager", tags=["gpt"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(optimization_monitoring_router, prefix="/optimization/monitoring", tags=["optimization"])
api_router.include_router(organization_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(organization_analytics_router, prefix="/organizations/analytics", tags=["organizations"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(resource_optimization_router, prefix="/resources/optimization", tags=["resources"])
api_router.include_router(resource_sharing_router, prefix="/resources/sharing", tags=["resources"])
api_router.include_router(security_router, prefix="/security", tags=["security"])
api_router.include_router(tool_registry_router, prefix="/tools", tags=["tools"])
api_router.include_router(user_preferences_router, prefix="/preferences", tags=["preferences"]) 
api_router.include_router(widget_export_router, prefix="", tags=["widget-export"])  # Prefix is already in router 