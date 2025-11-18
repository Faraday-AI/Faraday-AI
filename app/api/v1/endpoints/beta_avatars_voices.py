"""
FastAPI endpoints for Beta Avatars and Voices
Provides REST API for avatar and voice selection
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.beta_teacher_dashboard_service import BetaTeacherDashboardService

router = APIRouter(prefix="/beta", tags=["Beta Avatars & Voices"])


# ==================== BETA AVATARS ====================

@router.get("/avatars", response_model=List[Dict[str, Any]])
async def get_beta_avatars(
    voice_enabled: Optional[bool] = Query(None, description="Filter by voice enabled status"),
    db: Session = Depends(get_db)
):
    """Get all available beta avatars"""
    try:
        service = BetaTeacherDashboardService(db)
        return service.get_beta_avatars(voice_enabled)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting beta avatars: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving avatars: {str(e)}"
        )


@router.get("/avatars/{avatar_id}", response_model=Dict[str, Any])
async def get_beta_avatar(
    avatar_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific beta avatar"""
    service = BetaTeacherDashboardService(db)
    avatar = service.get_beta_avatar(avatar_id)
    
    if not avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )
    
    return avatar


# ==================== BETA VOICES ====================

@router.get("/voices", response_model=List[Dict[str, Any]])
async def get_beta_voices(
    avatar_id: Optional[str] = Query(None, description="Filter by avatar ID"),
    language: Optional[str] = Query(None, description="Filter by language code"),
    provider: Optional[str] = Query(None, description="Filter by voice provider"),
    limit: int = Query(500, ge=1, le=1000, description="Maximum number of voices to return"),
    offset: int = Query(0, ge=0, description="Number of voices to skip"),
    db: Session = Depends(get_db)
):
    """Get all available voices (320+ voices)"""
    try:
        service = BetaTeacherDashboardService(db)
        return service.get_beta_voices(avatar_id, language, provider, limit, offset)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting beta voices: {str(e)}", exc_info=True)
        # Return fallback voices instead of raising error
        try:
            service = BetaTeacherDashboardService(db)
            return service._get_fallback_voices(limit)
        except Exception as fallback_error:
            logger.error(f"Error getting fallback voices: {str(fallback_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving voices: {str(e)}"
            )

