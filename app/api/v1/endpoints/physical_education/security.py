from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.models.security import Token, SecurityRequest, SecurityResponse, ThreatAssessmentRequest, ThreatAssessmentResponse
from app.core.auth_models import User
from app.api.v1.middleware.auth import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user
)
from app.core.database import get_db
from app.core.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from app.services.physical_education.activity_security_manager import ActivitySecurityManager

router = APIRouter()
security_manager = ActivitySecurityManager()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login endpoint to get access and refresh tokens."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "scopes": user.scopes}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/token/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    current_user: User = Depends(get_current_active_user)
):
    """Refresh access token using refresh token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username, "scopes": payload.get("scopes", [])},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": username, "scopes": payload.get("scopes", [])}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": new_refresh_token
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        ) 