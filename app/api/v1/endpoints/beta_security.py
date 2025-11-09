"""
FastAPI endpoints for Beta Security Service
Provides REST API for security management in the beta teacher system
"""

from typing import List, Optional, Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.beta_security_service import BetaSecurityService
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration

router = APIRouter(prefix="/beta/security", tags=["Beta Security"])

# Export router for use in main app
__all__ = ['router']


# ==================== ACCESS VALIDATION ====================

@router.post("/validate-access", response_model=Dict[str, bool])
async def validate_access(
    user_id: Union[str, int],
    required_level: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate if a user has the required access level (beta teacher context)."""
    try:
        service = BetaSecurityService(db, current_teacher.id)
        has_access = await service.validate_access(user_id, required_level, db)
        return {"has_access": has_access}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating access: {str(e)}"
        )


# ==================== SECURITY EVENT LOGGING ====================

@router.post("/log-event", response_model=Dict[str, Any])
async def log_security_event(
    event_data: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a security-related event for beta teacher."""
    try:
        service = BetaSecurityService(db, current_teacher.id)
        return await service.log_security_event(
            event_type=event_data.get("event_type"),
            user_id=event_data.get("user_id"),
            details=event_data.get("details"),
            ip_address=event_data.get("ip_address"),
            resource_type=event_data.get("resource_type"),
            resource_id=event_data.get("resource_id"),
            action=event_data.get("action"),
            severity=event_data.get("severity", "info"),
            description=event_data.get("description"),
            success=event_data.get("success", "unknown"),
            db=db
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging security event: {str(e)}"
        )


# ==================== INPUT SANITIZATION ====================

@router.post("/sanitize", response_model=Dict[str, Any])
async def sanitize_input(
    input_data: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sanitize input data for beta teacher."""
    try:
        service = BetaSecurityService(db, current_teacher.id)
        input_value = input_data.get("input_data")
        input_type = input_data.get("input_type", "string")
        
        sanitized = await service.sanitize_input(input_value, input_type, db)
        return {
            "original": input_value,
            "sanitized": sanitized,
            "input_type": input_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sanitizing input: {str(e)}"
        )


# ==================== SECURITY EVENTS QUERY ====================

@router.get("/events", response_model=List[Dict[str, Any]])
async def get_security_events(
    limit: int = 100,
    offset: int = 0,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security events for beta teacher."""
    try:
        service = BetaSecurityService(db, current_teacher.id)
        return await service.get_security_events(
            limit=limit,
            offset=offset,
            event_type=event_type,
            severity=severity
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving security events: {str(e)}"
        )

