import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.core.auth_models import User
from app.core.config import get_settings
from sqlalchemy.orm import Session
from app.core.database import get_db

class TestOAuth2PasswordBearer(OAuth2PasswordBearer):
    """Custom OAuth2 scheme that bypasses authentication in test mode."""
    
    async def __call__(self, request):
        # Skip authentication in test mode
        if os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true":
            return "test_token"
        
        # Use the parent class implementation for normal operation
        return await super().__call__(request)

oauth2_scheme = TestOAuth2PasswordBearer(tokenUrl="token")
settings = get_settings()

async def verify_token(token: str, db: Session) -> User:
    """Verify JWT token and return the user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
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
    else:
        return User(
            username=username,
            email=f"{username}@example.com",
            full_name=f"User {username}",
            disabled=False,
            scopes=["activities:read"]
        )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token."""
    # Skip authentication in test mode
    if os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true":
        # Return a mock user for testing
        mock_user = User(
            username="test",
            email="test@example.com",
            full_name="Test User",
            disabled=False,
            scopes=["activities:read", "activities:write", "admin"]
        )
        return mock_user
    
    if isinstance(token, str):
        return await verify_token(token, db)
    return await verify_token(token.credentials, db)

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    # For now, return a mock user
    # In a real implementation, this would verify credentials against the database
    if username == "admin" and password == "admin":
        return User(
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            disabled=False,
            scopes=["activities:read", "activities:write", "admin"]
        )
    elif username == "teacher" and password == "teacher":
        return User(
            username="teacher",
            email="teacher@example.com",
            full_name="Teacher",
            disabled=False,
            scopes=["activities:read", "activities:write"]
        )
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Constants for token configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # Get from environment variables
ALGORITHM = "HS256" 