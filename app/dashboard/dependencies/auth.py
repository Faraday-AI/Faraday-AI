from typing import Optional, List, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dashboard.services.access_control_service import AccessControlService
from app.dashboard.schemas.access_control import ResourceType, ActionType
import jwt
from datetime import datetime, timedelta
import os

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthDependencies:
    def __init__(self, db: Session):
        self.db = db
        self.access_control = AccessControlService(db)

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> str:
        """Get the current user from the JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    def require_permission(
        self,
        resource_type: ResourceType,
        action: ActionType,
        resource_id: Optional[str] = None
    ):
        """Dependency to require specific permissions."""
        async def permission_checker(
            user_id: str = Depends(get_current_user),
            db: Session = Depends(get_db)
        ) -> bool:
            access_control = AccessControlService(db)
            has_permission = await access_control.check_permission(
                user_id=user_id,
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
            user_id: str = Depends(get_current_user),
            db: Session = Depends(get_db)
        ) -> bool:
            access_control = AccessControlService(db)
            for permission in permissions:
                has_permission = await access_control.check_permission(
                    user_id=user_id,
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
            user_id: str = Depends(get_current_user),
            db: Session = Depends(get_db)
        ) -> bool:
            access_control = AccessControlService(db)
            for permission in permissions:
                has_permission = await access_control.check_permission(
                    user_id=user_id,
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

# Create a global instance of AuthDependencies
auth_deps = AuthDependencies(get_db())

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
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        ) 