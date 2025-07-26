import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.dashboard.models import DashboardUser as User
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
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token."""
    # Skip authentication in test mode
    if os.getenv("TEST_MODE") == "true" or os.getenv("TESTING") == "true":
        # Return a mock user for testing
        mock_user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_active=True,
            role="admin"  # Give admin role for testing
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