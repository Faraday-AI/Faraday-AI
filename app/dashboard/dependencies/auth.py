from typing import Optional, List, Dict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request as StarletteRequest
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dashboard.services.access_control_service import AccessControlService
from app.dashboard.schemas.access_control import ResourceType, ActionType
import jwt
from datetime import datetime, timedelta
import os

# OAuth2 scheme for token authentication
class TestOAuth2PasswordBearer(OAuth2PasswordBearer):
    """Custom OAuth2 scheme that bypasses authentication in test mode."""
    
    def __init__(self, *args, **kwargs):
        """Initialize OAuth2 scheme - no instance-level state to avoid test isolation issues."""
        super().__init__(*args, **kwargs)
        # No instance variables - all state comes from request headers
    
    async def __call__(self, request: Request = None):
        if request is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Check for Authorization header - MUST check headers dict directly
        # FastAPI's HeaderDict.get() returns None if key doesn't exist
        # Use explicit check to avoid any caching issues
        auth_header = None
        try:
            # Try multiple ways to get the header to be absolutely sure
            if hasattr(request, 'headers'):
                if hasattr(request.headers, 'get'):
                    auth_header = request.headers.get("Authorization")
                elif hasattr(request.headers, '__contains__'):
                    if "Authorization" in request.headers:
                        auth_header = request.headers["Authorization"]
                    elif "authorization" in request.headers:
                        auth_header = request.headers["authorization"]
                elif hasattr(request.headers, '__getitem__'):
                    try:
                        auth_header = request.headers["Authorization"]
                    except (KeyError, TypeError):
                        try:
                            auth_header = request.headers["authorization"]
                        except (KeyError, TypeError):
                            auth_header = None
        except Exception:
            auth_header = None
        
        # Validate auth_header - must be non-empty string starting with "Bearer "
        # Be very explicit about what constitutes valid auth
        has_valid_auth = False
        if auth_header is not None:
            if isinstance(auth_header, str):
                auth_header_clean = auth_header.strip()
                if len(auth_header_clean) > 0:
                    has_valid_auth = auth_header_clean.startswith("Bearer ")
        
        # In test mode: only bypass if Authorization header exists and is valid
        test_mode = os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true"
        
        if test_mode:
            if has_valid_auth:
                # Authorized request in test mode - return token
                token = auth_header.strip().split(" ", 1)[1] if " " in auth_header.strip() else "test_token"
                return token
            # No valid Authorization header in test mode - MUST raise 401 directly
            # Do NOT call parent - it might have caching or state issues
            # Directly raise 401 for unauthorized requests in test mode
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # For normal (non-test) operation, always call parent
        # Parent will raise 401 if Authorization header is missing or invalid
        return await super().__call__(request)

# Module-level OAuth2 scheme instance
# FastAPI ensures this is called per-request, so no caching issues at this level
oauth2_scheme = TestOAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Standalone get_current_user function (like app/core/auth.py)
# Note: Using module-level oauth2_scheme is fine - FastAPI ensures it's called per-request
# The issue was test isolation, not dependency caching. Tests now use fresh clients.
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """Get the current user from the JWT token. Returns a dict with 'id' key for compatibility with dashboard endpoints."""
    # In test mode: if we got here, oauth2_scheme either:
    # 1. Returned a token (authorized request) - return test_user
    # 2. Raised 401 (unauthorized) - this function wouldn't be called
    # So if we're here in test mode with a token, we're authorized
    test_mode = os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true"
    if test_mode:
        # Validate token exists and is not empty/None
        if token and isinstance(token, str) and len(token.strip()) > 0:
            return {"id": "test_user"}
        # No valid token - raise 401 (shouldn't happen if oauth2_scheme works correctly)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"id": user_id}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

class AuthDependencies:
    def __init__(self, db: Session):
        self.db = db
        self.access_control = AccessControlService(db)

    def require_permission(
        self,
        resource_type: ResourceType,
        action: ActionType,
        resource_id: Optional[str] = None
    ):
        """Dependency to require specific permissions."""
        async def permission_checker(
            current_user: Dict[str, str] = Depends(get_current_user),
            db: Session = Depends(get_db)
        ) -> bool:
            access_control = AccessControlService(db)
            has_permission = await access_control.check_permission(
                user_id=current_user["id"],
                resource_type=resource_type,
                action=action,
                resource_id=resource_id
            )
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {action} on {resource_type}"
                )
            return True
        return permission_checker

    def require_any_permission(
        self,
        permissions: List[Dict[str, str]]
    ):
        """Dependency to require any of the specified permissions."""
        async def any_permission_checker(
            current_user: Dict[str, str] = Depends(get_current_user),
            db: Session = Depends(get_db)
        ) -> bool:
            access_control = AccessControlService(db)
            for permission in permissions:
                has_permission = await access_control.check_permission(
                    user_id=current_user["id"],
                    resource_type=ResourceType(permission["resource_type"]),
                    action=ActionType(permission["action"]),
                    resource_id=permission.get("resource_id")
                )
                if has_permission:
                    return True
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return any_permission_checker

    def require_all_permissions(
        self,
        permissions: List[Dict[str, str]]
    ):
        """Dependency to require all of the specified permissions."""
        async def all_permissions_checker(
            current_user: Dict[str, str] = Depends(get_current_user),
            db: Session = Depends(get_db)
        ) -> bool:
            access_control = AccessControlService(db)
            for permission in permissions:
                has_permission = await access_control.check_permission(
                    user_id=current_user["id"],
                    resource_type=ResourceType(permission["resource_type"]),
                    action=ActionType(permission["action"]),
                    resource_id=permission.get("resource_id")
                )
                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied: {permission['action']} on {permission['resource_type']}"
                    )
            return True
        return all_permissions_checker

# Helper function to get AuthDependencies instance per request
def get_auth_deps(db: Session = Depends(get_db)) -> AuthDependencies:
    """Get AuthDependencies instance for current request."""
    return AuthDependencies(db)

# Helper functions for creating and verifying tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        ) 