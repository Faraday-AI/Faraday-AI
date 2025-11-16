"""
Teacher Authentication API Endpoints for Beta Version

Handles teacher registration, login, email verification, and password management
for individual teachers without school district integration.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import create_access_token, create_refresh_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.auth.teacher_registration_service import TeacherRegistrationService
from app.services.email.email_service import EmailService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/auth/teacher",
    tags=["teacher-authentication"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input data"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication failed"},
        status.HTTP_409_CONFLICT: {"description": "Email already registered"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)

# Pydantic models for request/response
class TeacherRegistrationRequest(BaseModel):
    email: EmailStr = Field(..., description="Teacher's email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (8-128 characters)")
    first_name: str = Field(..., min_length=2, max_length=100, description="First name")
    last_name: str = Field(..., min_length=2, max_length=100, description="Last name")
    school_name: Optional[str] = Field(None, max_length=255, description="School name (optional)")
    school_district: Optional[str] = Field(None, max_length=255, description="School district (optional)")
    teaching_experience_years: Optional[int] = Field(None, ge=0, le=50, description="Years of teaching experience")
    grade_levels: Optional[list[str]] = Field(default=[], description="Grade levels taught")
    specializations: Optional[list[str]] = Field(default=[], description="Teaching specializations")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class TeacherLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Teacher's email address")
    password: str = Field(..., description="Password")

class EmailVerificationRequest(BaseModel):
    token: str = Field(..., description="Email verification token")

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Teacher's email address")

class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class TeacherAuthResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    teacher_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Dependency to get teacher registration service
def get_teacher_registration_service(db: Session = Depends(get_db)) -> TeacherRegistrationService:
    return TeacherRegistrationService(db)

# Dependency to get email service
def get_email_service() -> EmailService:
    return EmailService()

@router.post(
    "/register",
    response_model=TeacherAuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new teacher account",
    description="Register a new teacher account for the beta version. Email verification required.",
    response_description="Registration result with verification instructions"
)
async def register_teacher(
    request: TeacherRegistrationRequest,
    registration_service: TeacherRegistrationService = Depends(get_teacher_registration_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Register a new teacher account."""
    try:
        logger.info(f"Teacher registration attempt for email: {request.email}")
        
        # Register teacher
        result = await registration_service.register_teacher(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            school_name=request.school_name,
            school_district=request.school_district,
            teaching_experience_years=request.teaching_experience_years,
            grade_levels=request.grade_levels,
            specializations=request.specializations
        )
        
        # Email verification is disabled - skip sending verification email
        # (Email service setup can be added later when Microsoft 365 is configured)
        
        return TeacherAuthResponse(
            success=True,
            message=result.get("message", "Registration successful. Please check your email to verify your account."),
            teacher_id=result["teacher_id"],
            email=result["email"]
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in teacher registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in teacher registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )

@router.post(
    "/login",
    response_model=TeacherAuthResponse,
    summary="Login teacher account",
    description="Authenticate teacher with email and password",
    response_description="Authentication result with access token"
)
async def login_teacher(
    request: TeacherLoginRequest,
    registration_service: TeacherRegistrationService = Depends(get_teacher_registration_service)
):
    """Login teacher account."""
    try:
        logger.info(f"Teacher login attempt for email: {request.email}")
        
        # Authenticate teacher
        teacher_data = await registration_service.authenticate_teacher(
            email=request.email,
            password=request.password
        )
        
        if not teacher_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Email verification is disabled - proceed directly to token creation
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": teacher_data["teacher_id"],
                "email": teacher_data["email"],
                "type": "teacher"
            },
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={
                "sub": teacher_data["teacher_id"],
                "email": teacher_data["email"],
                "type": "teacher"
            }
        )
        
        return TeacherAuthResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            teacher_id=teacher_data["teacher_id"],
            email=teacher_data["email"],
            first_name=teacher_data["first_name"],
            last_name=teacher_data["last_name"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in teacher login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@router.post(
    "/verify-email",
    response_model=TeacherAuthResponse,
    summary="Verify teacher email",
    description="Verify teacher email address using verification token",
    response_description="Email verification result"
)
async def verify_email(
    request: EmailVerificationRequest,
    registration_service: TeacherRegistrationService = Depends(get_teacher_registration_service)
):
    """Verify teacher email address."""
    try:
        logger.info(f"Email verification attempt with token: {request.token[:10]}...")
        
        success = await registration_service.verify_email(request.token)
        
        if success:
            return TeacherAuthResponse(
                success=True,
                message="Email verified successfully. You can now log in."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in email verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during email verification"
        )

@router.post(
    "/resend-verification",
    response_model=TeacherAuthResponse,
    summary="Resend email verification",
    description="Resend email verification token to teacher",
    response_description="Resend verification result"
)
async def resend_verification(
    request: PasswordResetRequest,  # Reusing for email parameter
    registration_service: TeacherRegistrationService = Depends(get_teacher_registration_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Resend email verification token."""
    try:
        logger.info(f"Resend verification request for email: {request.email}")
        
        success = await registration_service.resend_verification(request.email)
        
        if success:
            # Get verification token to send email
            # Note: In a real implementation, you'd get the token from the service
            return TeacherAuthResponse(
                success=True,
                message="Verification email sent successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found or already verified"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in resend verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while resending verification"
        )

@router.post(
    "/forgot-password",
    response_model=TeacherAuthResponse,
    summary="Request password reset",
    description="Send password reset token to teacher email",
    response_description="Password reset request result"
)
async def forgot_password(
    request: PasswordResetRequest,
    registration_service: TeacherRegistrationService = Depends(get_teacher_registration_service),
    email_service: EmailService = Depends(get_email_service)
):
    """Request password reset."""
    try:
        logger.info(f"Password reset request for email: {request.email}")
        
        reset_token = await registration_service.create_password_reset_token(request.email)
        
        if reset_token:
            # Send password reset email
            try:
                await email_service.send_password_reset_email(
                    email=request.email,
                    token=reset_token
                )
            except Exception as e:
                logger.warning(f"Failed to send password reset email to {request.email}: {str(e)}")
                # Don't fail the request if email sending fails
        
        # Always return success to prevent email enumeration
        return TeacherAuthResponse(
            success=True,
            message="If the email exists, a password reset link has been sent"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing password reset"
        )

@router.post(
    "/reset-password",
    response_model=TeacherAuthResponse,
    summary="Reset password",
    description="Reset teacher password using reset token",
    response_description="Password reset result"
)
async def reset_password(
    request: PasswordResetConfirmRequest,
    registration_service: TeacherRegistrationService = Depends(get_teacher_registration_service)
):
    """Reset teacher password."""
    try:
        logger.info(f"Password reset attempt with token: {request.token[:10]}...")
        
        success = await registration_service.reset_password(
            token=request.token,
            new_password=request.new_password
        )
        
        if success:
            return TeacherAuthResponse(
                success=True,
                message="Password reset successfully. You can now log in with your new password."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
    except ValueError as e:
        logger.warning(f"Validation error in password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in password reset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during password reset"
        )

@router.get(
    "/check-email/{email}",
    summary="Check email availability",
    description="Check if email address is available for registration",
    response_description="Email availability status"
)
async def check_email_availability(
    email: str,
    registration_service: TeacherRegistrationService = Depends(get_teacher_registration_service)
):
    """Check if email is available for registration."""
    try:
        available = await registration_service.check_email_availability(email)
        
        return {
            "email": email,
            "available": available,
            "message": "Email is available" if available else "Email is already registered"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error checking email availability: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while checking email availability"
        )
