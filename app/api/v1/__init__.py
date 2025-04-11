from fastapi import APIRouter
from .endpoints import activity, visualization, collaboration, security
from .middleware import auth, rate_limit

# Create main router
router = APIRouter()

# Include all routers
router.include_router(activity.router, prefix="/api/v1", tags=["activities"])
router.include_router(visualization.router, prefix="/api/v1", tags=["visualizations"])
router.include_router(collaboration.router, prefix="/api/v1", tags=["collaboration"])
router.include_router(security.router, prefix="/api/v1", tags=["security"])

# Add middleware
router.middleware("http")(auth.add_authentication)
router.middleware("http")(rate_limit.add_rate_limiting) 