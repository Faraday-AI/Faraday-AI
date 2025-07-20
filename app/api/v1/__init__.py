from fastapi import APIRouter
from .endpoints import activity_router, ai_analysis_router, lesson_plans_router, pe_router, user_profile_router, user_preferences_router
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

# Export middleware functions for use in main FastAPI app
authentication_middleware = auth.add_authentication
rate_limiting_middleware = rate_limit.add_rate_limiting 