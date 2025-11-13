"""
Microsoft/Azure AD Authentication API Endpoints for Beta System

Handles Microsoft OAuth authentication flow for beta teachers.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta

from app.core.database import get_db
from app.core.auth import create_access_token, create_refresh_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.services.integration.msgraph_service import get_msgraph_service, MSGraphService
from app.models.teacher_registration import TeacherRegistration
from app.core.auth_models import User

logger = logging.getLogger(__name__)

# Helper function to get beta teacher from user
def get_current_beta_teacher(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeacherRegistration:
    """Get the current beta teacher from the authenticated user."""
    if not current_user or not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    
    teacher = db.query(TeacherRegistration).filter(
        TeacherRegistration.email == current_user.email,
        TeacherRegistration.is_active == True
    ).first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a registered beta teacher"
        )
    
    return teacher

# Initialize router
router = APIRouter(
    prefix="/beta/auth/microsoft",
    tags=["beta-microsoft-authentication"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication failed"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

# Response models
class MicrosoftAuthResponse(BaseModel):
    success: bool
    message: str
    auth_url: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    teacher_id: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None

@router.get(
    "/",
    response_model=MicrosoftAuthResponse,
    summary="Initiate Microsoft/Azure AD login for beta teachers",
    description="Redirects to Microsoft OAuth login page or returns authorization URL"
)
async def initiate_microsoft_login_beta(
    request: Request,
    db: Session = Depends(get_db)
):
    """Initiate Microsoft/Azure AD authentication flow for beta teachers."""
    try:
        msgraph_service = get_msgraph_service()
        
        if not msgraph_service.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Microsoft Graph service not configured. Please set MSCLIENTID, MSCLIENTSECRET, and MSTENANTID environment variables."
            )
        
        # Get authorization URL
        auth_url = msgraph_service.get_auth_url()
        
        # Check if request wants JSON response (API call) or redirect (web browser)
        accept_header = request.headers.get("Accept", "")
        if "application/json" in accept_header:
            return MicrosoftAuthResponse(
                success=True,
                message="Redirect to this URL to authenticate with Microsoft",
                auth_url=auth_url
            )
        else:
            # Redirect browser to Microsoft login
            return RedirectResponse(url=auth_url)
            
    except ValueError as e:
        logger.error(f"Microsoft authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error initiating Microsoft login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Microsoft authentication"
        )

@router.get(
    "/callback",
    response_model=MicrosoftAuthResponse,
    summary="Handle Microsoft OAuth callback for beta teachers",
    description="Handles OAuth callback from Microsoft and creates/updates beta teacher account"
)
async def microsoft_callback_beta(
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Microsoft OAuth callback and create JWT tokens for beta teachers."""
    try:
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided"
            )
        
        msgraph_service = get_msgraph_service()
        
        if not msgraph_service.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Microsoft Graph service not configured"
            )
        
        # Exchange authorization code for access token
        token_result = msgraph_service.get_token(code)
        
        if token_result.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=token_result.get("error", "Failed to authenticate with Microsoft")
            )
        
        token_data = token_result.get("token", {})
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to obtain access token from Microsoft"
            )
        
        # Get user information from Microsoft Graph
        user_info_result = msgraph_service.get_user_info(access_token)
        
        if user_info_result.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to retrieve user information from Microsoft"
            )
        
        user_data = user_info_result.get("data", {})
        microsoft_email = user_data.get("mail") or user_data.get("userPrincipalName")
        microsoft_id = user_data.get("id")
        display_name = user_data.get("displayName", "")
        
        if not microsoft_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Microsoft account does not have an email address"
            )
        
        # Find or create beta teacher in database
        from app.models.teacher_registration import TeacherRegistration
        import uuid
        
        teacher = db.query(TeacherRegistration).filter(
            TeacherRegistration.email == microsoft_email
        ).first()
        
        if not teacher:
            # Create new beta teacher from Microsoft account
            teacher = TeacherRegistration(
                id=str(uuid.uuid4()),
                email=microsoft_email,
                is_active=True,
                email_verified=True  # Microsoft email is already verified
            )
            db.add(teacher)
            db.flush()
            db.refresh(teacher)
            logger.info(f"Created new beta teacher from Microsoft account: {microsoft_email}")
        else:
            # Update existing teacher
            teacher.is_active = True
            teacher.email_verified = True
            db.flush()
            logger.info(f"Updated existing beta teacher from Microsoft account: {microsoft_email}")
        
        # Store Microsoft OAuth tokens with encryption
        from app.models.integration.microsoft_token import BetaMicrosoftOAuthToken
        from app.services.integration.token_encryption import get_token_encryption_service
        from datetime import datetime, timedelta
        
        # Encrypt tokens before storing
        encryption_service = get_token_encryption_service()
        access_token_plain = token_data.get("access_token", "")
        refresh_token_plain = token_data.get("refresh_token")
        id_token_plain = token_data.get("id_token")
        
        # Encrypt tokens
        encrypted_access_token = encryption_service.encrypt(access_token_plain) if access_token_plain else ""
        encrypted_refresh_token = encryption_service.encrypt(refresh_token_plain) if refresh_token_plain else None
        encrypted_id_token = encryption_service.encrypt(id_token_plain) if id_token_plain else None
        
        # Calculate token expiration (MSAL returns expires_in in seconds)
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Store or update Microsoft OAuth token
        oauth_token = db.query(BetaMicrosoftOAuthToken).filter(
            BetaMicrosoftOAuthToken.teacher_id == teacher.id
        ).first()
        
        if oauth_token:
            # Update existing token
            oauth_token.access_token = encrypted_access_token
            oauth_token.refresh_token = encrypted_refresh_token or oauth_token.refresh_token
            oauth_token.id_token = encrypted_id_token or oauth_token.id_token
            oauth_token.token_type = token_data.get("token_type", "Bearer")
            oauth_token.expires_at = expires_at
            oauth_token.scope = " ".join(token_data.get("scope", [])) if isinstance(token_data.get("scope"), list) else token_data.get("scope", "")
            oauth_token.microsoft_id = microsoft_id
            oauth_token.microsoft_email = microsoft_email
            oauth_token.is_active = True
            oauth_token.last_used_at = datetime.utcnow()
            oauth_token.updated_at = datetime.utcnow()
        else:
            # Create new token record
            oauth_token = BetaMicrosoftOAuthToken(
                teacher_id=teacher.id,
                access_token=encrypted_access_token,
                refresh_token=encrypted_refresh_token,
                id_token=encrypted_id_token,
                token_type=token_data.get("token_type", "Bearer"),
                expires_at=expires_at,
                scope=" ".join(token_data.get("scope", [])) if isinstance(token_data.get("scope"), list) else token_data.get("scope", ""),
                microsoft_id=microsoft_id,
                microsoft_email=microsoft_email,
                is_active=True,
                last_used_at=datetime.utcnow()
            )
            db.add(oauth_token)
        
        db.commit()
        logger.info(f"Stored Microsoft OAuth token for beta teacher {teacher.id}")
        
        # Create JWT tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_access_token = create_access_token(
            data={
                "sub": str(teacher.id),  # Convert UUID to string for JWT encoding
                "email": teacher.email,
                "type": "teacher"
            },
            expires_delta=access_token_expires
        )
        
        jwt_refresh_token = create_refresh_token(
            data={
                "sub": str(teacher.id),  # Convert UUID to string for JWT encoding
                "email": teacher.email,
                "type": "teacher"
            }
        )
        
        return MicrosoftAuthResponse(
            success=True,
            message="Successfully authenticated with Microsoft",
            access_token=jwt_access_token,
            refresh_token=jwt_refresh_token,
            teacher_id=str(teacher.id),  # Convert UUID to string for JSON serialization
            user_info={
                "id": str(teacher.id),  # Convert UUID to string
                "email": teacher.email,
                "microsoft_id": microsoft_id,
                "display_name": display_name
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Microsoft callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete Microsoft authentication"
        )

@router.get(
    "/user",
    summary="Get Microsoft user information for beta teacher",
    description="Get current beta teacher's Microsoft account information"
)
async def get_microsoft_user_info_beta(
    current_teacher: TeacherRegistration = Depends(get_current_beta_teacher),
    db: Session = Depends(get_db)
):
    """Get Microsoft user information for authenticated beta teacher."""
    try:
        msgraph_service = get_msgraph_service()
        
        # This endpoint would require storing Microsoft access tokens
        # For now, return basic teacher info
        return {
            "success": True,
            "teacher": {
                "id": str(current_teacher.id),  # Convert UUID to string
                "email": current_teacher.email
            },
            "message": "Microsoft integration available. Use /beta/auth/microsoft to authenticate."
        }
    except Exception as e:
        logger.error(f"Error getting Microsoft user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Microsoft user information"
        )

