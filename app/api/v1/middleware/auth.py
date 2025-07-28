import os
from fastapi import Request, HTTPException, status, Security, Depends
from fastapi.security import SecurityScopes
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.auth_models import TokenData, User
from app.core.database import get_db
from app.core.config import settings

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # Get from environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "activities:read": "Read activities",
        "activities:write": "Write activities",
        "visualizations:read": "Read visualizations",
        "visualizations:write": "Write visualizations",
        "collaboration:read": "Read collaboration sessions",
        "collaboration:write": "Write collaboration sessions"
    }
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["activities:read"])
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_user(username: str) -> Optional[User]:
    """Get user by username."""
    # For now, return a mock user
    # In a real implementation, this would query the database
    if username == "admin":
        return User(
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            disabled=False,
            scopes=["activities:read", "activities:write", "admin"]
        )
    elif username == "teacher":
        return User(
            username="teacher",
            email="teacher@example.com",
            full_name="Teacher",
            disabled=False,
            scopes=["activities:read", "activities:write"]
        )
    else:
        return User(
            username=username,
            email=f"{username}@example.com",
            full_name=f"User {username}",
            disabled=False,
            scopes=["activities:read"]
        )

async def get_current_admin_user(
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    """Get current admin user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def add_authentication(request: Request, call_next):
    if request.url.path not in ["/token", "/docs", "/openapi.json"]:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )
            await get_current_user(SecurityScopes([]), token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    response = await call_next(request)
    return response 