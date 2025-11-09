"""
FastAPI endpoints for Beta Context Analytics Service
Provides REST API for context analytics in the beta teacher system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.beta_context_analytics_service import BetaContextAnalyticsService
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration

router = APIRouter(prefix="/beta/contexts", tags=["Beta Context Analytics"])

# Export router for use in main app
__all__ = ['router']


# ==================== CONTEXTS ====================

@router.get("", response_model=List[Dict[str, Any]])
async def get_contexts(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get GPT context records for beta teacher."""
    try:
        service = BetaContextAnalyticsService(db, current_teacher.id)
        return await service.get_contexts(
            is_active=is_active,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving contexts: {str(e)}"
        )


@router.post("", response_model=Dict[str, Any])
async def create_context(
    context_data: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new GPT context for beta teacher."""
    try:
        service = BetaContextAnalyticsService(db, current_teacher.id)
        return await service.create_context(context_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating context: {str(e)}"
        )


# ==================== CONTEXT INTERACTIONS ====================

@router.get("/interactions", response_model=List[Dict[str, Any]])
async def get_context_interactions(
    context_id: Optional[int] = Query(None, description="Filter by context ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get context interaction records for beta teacher."""
    try:
        service = BetaContextAnalyticsService(db, current_teacher.id)
        return await service.get_context_interactions(
            context_id=context_id,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving context interactions: {str(e)}"
        )


# ==================== CONTEXT METRICS ====================

@router.get("/metrics", response_model=List[Dict[str, Any]])
async def get_context_metrics(
    context_id: Optional[int] = Query(None, description="Filter by context ID"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get context metrics records for beta teacher."""
    try:
        service = BetaContextAnalyticsService(db, current_teacher.id)
        return await service.get_context_metrics(
            context_id=context_id,
            metric_type=metric_type,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving context metrics: {str(e)}"
        )


# ==================== MIGRATION STATUS ====================

@router.get("/migration-status", response_model=Dict[str, int])
async def get_migration_status(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get migration status for beta teacher's context data."""
    try:
        service = BetaContextAnalyticsService(db, current_teacher.id)
        return await service.migrate_existing_context_data()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving migration status: {str(e)}"
        )

