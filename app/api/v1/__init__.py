from fastapi import APIRouter
from .endpoints import activity_router, ai_analysis_router, lesson_plans_router, pe_router, user_profile_router, user_preferences_router, role_management_router, permission_management_router, organization_management_router, team_management_router, user_analytics_router, beta_testing_router
from .endpoints import resource_management, beta_teacher_dashboard, beta_safety, beta_assessment, beta_security, beta_resource_management, dashboard_resource_management, dashboard_context_analytics, beta_context_analytics, dashboard_preferences, beta_dashboard_preferences
from .endpoints import microsoft_auth, beta_microsoft_auth, microsoft_calendar, beta_microsoft_calendar, microsoft_health, speech_to_text, guest_chat
from .middleware import auth, rate_limit

# Create main router
router = APIRouter()

# Include all routers
router.include_router(activity_router, prefix="/api/v1", tags=["activities"])
router.include_router(ai_analysis_router, prefix="/api/v1", tags=["ai-analysis"])
router.include_router(lesson_plans_router, prefix="/api/v1", tags=["lesson-plans"])
router.include_router(pe_router, prefix="/api/v1", tags=["physical-education"])
router.include_router(user_profile_router, prefix="/api/v1/users", tags=["user-profiles"])
router.include_router(user_preferences_router, prefix="/api/v1/users", tags=["user-preferences"])
router.include_router(role_management_router, prefix="/api/v1/roles", tags=["role-management"])
router.include_router(permission_management_router, prefix="/api/v1/permissions", tags=["permission-management"])
router.include_router(organization_management_router, prefix="/api/v1/organizations", tags=["organization-management"])
router.include_router(team_management_router, prefix="/api/v1/teams", tags=["team-management"])
router.include_router(user_analytics_router, prefix="/api/v1/analytics", tags=["user-analytics"])
router.include_router(beta_testing_router, prefix="/api/v1/beta-testing", tags=["beta-testing"])
router.include_router(resource_management.router, prefix="/api/v1")
router.include_router(beta_teacher_dashboard.router, prefix="/api/v1")
router.include_router(beta_safety.router, prefix="/api/v1")
router.include_router(beta_assessment.router, prefix="/api/v1")
router.include_router(beta_security.router, prefix="/api/v1")
router.include_router(beta_resource_management.router, prefix="/api/v1")
router.include_router(dashboard_resource_management.router, prefix="/api/v1")
router.include_router(dashboard_context_analytics.router, prefix="/api/v1")
router.include_router(beta_context_analytics.router, prefix="/api/v1")
router.include_router(dashboard_preferences.router, prefix="/api/v1")
router.include_router(beta_dashboard_preferences.router, prefix="/api/v1")
# Microsoft integration routers
# CRITICAL: Log router inclusion to verify it happens
import sys
print(f"app/api/v1/__init__.py: Including microsoft_auth router with prefix=/api/v1", file=sys.stderr, flush=True)
import logging
logger = logging.getLogger(__name__)
logger.info(f"Including microsoft_auth router with prefix=/api/v1")
router.include_router(microsoft_auth.router, prefix="/api/v1", tags=["microsoft-authentication"])
print(f"app/api/v1/__init__.py: microsoft_auth router included, routes: {[r.path for r in microsoft_auth.router.routes]}", file=sys.stderr, flush=True)
router.include_router(beta_microsoft_auth.router, prefix="/api/v1", tags=["beta-microsoft-authentication"])
router.include_router(microsoft_calendar.router, prefix="/api/v1", tags=["microsoft-calendar"])
router.include_router(beta_microsoft_calendar.router, prefix="/api/v1", tags=["beta-microsoft-calendar"])
router.include_router(microsoft_health.router, prefix="/api/v1", tags=["microsoft-health"])
# Speech-to-text router - include with /api/v1 prefix to match other routes
router.include_router(speech_to_text.router, prefix="/api/v1", tags=["speech-to-text"])
# Guest chat router - allows chat without authentication
router.include_router(guest_chat.router, prefix="/api/v1", tags=["guest-chat"])

# Export middleware functions for use in main FastAPI app
authentication_middleware = auth.add_authentication
rate_limiting_middleware = rate_limit.add_rate_limiting 