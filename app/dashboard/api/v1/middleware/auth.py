"""Authentication middleware for access control endpoints."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .....core.auth import get_current_user

security = HTTPBearer()

async def verify_access_control_auth(request: Request, credentials: HTTPAuthorizationCredentials = None):
    """Verify authentication for access control endpoints."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials"
        )
    
    try:
        token = credentials.credentials
        user = await get_current_user(token)
        request.state.user = user
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

def setup_auth_middleware(app):
    """Set up authentication middleware for access control endpoints."""
    
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        if "/api/v1/access-control" in request.url.path:
            auth = await security(request)
            await verify_access_control_auth(request, auth)
        
        response = await call_next(request)
        return response 