"""
App factory for creating fresh FastAPI instances in tests.

This module provides a factory function to create a new FastAPI app instance
for each test, ensuring complete isolation between tests.
"""
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import get_settings

logger = logging.getLogger(__name__)

def create_test_app() -> FastAPI:
    """
    Create a fresh FastAPI application instance for testing.
    
    This function creates a new app instance with all routers and middleware,
    ensuring complete isolation between tests. Each test gets its own app instance
    with its own dependency_overrides dictionary.
    
    Returns:
        Configured FastAPI application instance ready for testing
    """
    # Create a new FastAPI instance
    app_instance = FastAPI(
        title="Faraday AI Educational Platform (Test)",
        description="AI-powered educational platform - Test Instance",
        version="1.0.0"
    )
    
    # Import all routers (they're already defined, we just need to include them)
    from app.api.v1 import router as api_router
    from app.api.auth import router as auth_router
    from app.api.v1.endpoints.core.memory import router as memory_router
    from app.api.v1.endpoints.assistants.math_assistant import router as math_assistant_router
    from app.api.v1.endpoints.assistants.science_assistant import router as science_assistant_router
    from app.api.v1.endpoints.physical_education import pe_router
    from app.api.v1.endpoints.physical_education.health_fitness import router as health_fitness_router
    from app.api.v1.endpoints.physical_education.activity_recommendations import router as activity_recommendations_router
    from app.api.v1.endpoints.management.ai_analysis import router as ai_analysis_router
    from app.api.v1.endpoints.management.activity_management import router as activity_management
    from app.api.v1.endpoints.user_analytics import router as user_analytics_router
    from app.api.v1.endpoints.beta_students import router as beta_students_router
    from app.api.v1.endpoints.rbac_management import router as rbac_management_router
    from app.api.v1.endpoints import educational
    from app.core.health import router as health_router
    from app.dashboard.api.v1.endpoints import (
        dashboard,
        analytics,
        compatibility,
        gpt_context,
        gpt_manager,
        resource_optimization,
        access_control,
        resource_sharing,
        optimization_monitoring,
        notifications
    )
    from app.dashboard.api.v1.endpoints import api_router as dashboard_api_router
    
    # Create debug router
    from fastapi import APIRouter, Request, HTTPException
    from fastapi.responses import JSONResponse
    debug_router = APIRouter(prefix="/api/debug", tags=["debug"])

    @debug_router.get("/paths", include_in_schema=True)
    async def debug_paths(request: Request):
        """Debug endpoint to check file paths."""
        try:
            static_path = Path("app/static")
            services_path = static_path / "services"
            phys_ed_path = services_path / "phys-ed.html"
            
            result = {
                "static_path_exists": static_path.exists(),
                "services_path_exists": services_path.exists(),
                "phys_ed_path_exists": phys_ed_path.exists(),
                "static_path": str(static_path),
                "services_path": str(services_path),
                "phys_ed_path": str(phys_ed_path),
            }
            return JSONResponse(content=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Include all routers
    app_instance.include_router(memory_router, prefix="/api/v1/memory", tags=["memory"])
    app_instance.include_router(math_assistant_router, prefix="/api/v1/math", tags=["math"])
    app_instance.include_router(science_assistant_router, prefix="/api/v1/science", tags=["science"])
    app_instance.include_router(health_router, tags=["System"])
    app_instance.include_router(ai_analysis_router, prefix="/api")
    app_instance.include_router(debug_router)
    app_instance.include_router(activity_management, prefix="/api/v1/activities", tags=["activities"])
    app_instance.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
    app_instance.include_router(dashboard_api_router, prefix="/api/v1/dashboard", tags=["dashboard"])
    app_instance.include_router(api_router)
    app_instance.include_router(user_analytics_router, prefix="/api/v1/analytics", tags=["user-analytics"])
    app_instance.include_router(analytics.router, prefix="/api/v1/dashboard/analytics", tags=["analytics"])
    app_instance.include_router(compatibility.router, prefix="/api/v1/compatibility", tags=["compatibility"])
    app_instance.include_router(gpt_context.router, prefix="/api/v1/gpt-context", tags=["gpt-context"])
    app_instance.include_router(gpt_manager.router, prefix="/api/v1/gpt-manager", tags=["gpt-manager"])
    app_instance.include_router(resource_optimization.router, prefix="/api/v1/resource-optimization", tags=["resource-optimization"])
    app_instance.include_router(access_control.router, prefix="/api/v1/access-control", tags=["access-control"])
    app_instance.include_router(resource_sharing.router, prefix="/api/v1/resource-sharing", tags=["resource-sharing"])
    app_instance.include_router(optimization_monitoring.router, prefix="/api/v1/optimization-monitoring", tags=["optimization-monitoring"])
    app_instance.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
    app_instance.include_router(educational.router, prefix="/api/v1/educational", tags=["educational"])
    app_instance.include_router(pe_router, prefix="/api/v1/phys-ed", tags=["physical-education"])
    app_instance.include_router(health_fitness_router, prefix="/api/v1/physical-education", tags=["physical-education"])
    app_instance.include_router(activity_recommendations_router, prefix="/api/v1/physical-education", tags=["physical-education"])
    app_instance.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app_instance.include_router(beta_students_router, prefix="/api/v1", tags=["beta"])
    app_instance.include_router(rbac_management_router, prefix="/api/v1/rbac-management", tags=["rbac-management"])
    
    # Mount static files (if they exist)
    base_dir = Path(__file__).parent.parent
    static_dir = Path("/app/static")
    if not static_dir.exists():
        static_dir = base_dir / "static"
    if static_dir.exists():
        app_instance.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Configure CORS
    app_settings = get_settings()
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.CORS_ORIGINS,
        allow_credentials=app_settings.CORS_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Set up rate limiting and auth middleware (minimal setup for tests)
    try:
        from app.dashboard.api.v1.middleware.rate_limit import setup_rate_limiting
        from app.dashboard.api.v1.middleware.auth import setup_auth_middleware
        setup_rate_limiting(app_instance)
        setup_auth_middleware(app_instance)
    except Exception as e:
        logger.warning(f"Could not set up rate limiting/auth middleware in test app: {e}")
    
    # Ensure limiter exists on app.state for tests
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    if not hasattr(app_instance.state, 'limiter'):
        app_instance.state.limiter = Limiter(key_func=get_remote_address)
    
    logger.info(f"Created fresh test app instance: {id(app_instance)}")
    return app_instance

