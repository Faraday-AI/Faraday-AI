"""
FastAPI endpoints for Beta Resource Management Service
Provides REST API for resource management in the beta teacher system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.beta_resource_management_service import BetaResourceManagementService
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration

router = APIRouter(prefix="/beta/resources", tags=["Beta Resource Management"])

# Export router for use in main app
__all__ = ['router']


# ==================== RESOURCE USAGE ====================

@router.get("/usage", response_model=List[Dict[str, Any]])
async def get_resource_usage(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource usage records for beta teacher."""
    try:
        service = BetaResourceManagementService(db, current_teacher.id)
        return await service.get_resource_usage(
            project_id=project_id,
            resource_type=resource_type,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resource usage: {str(e)}"
        )


@router.post("/usage", response_model=Dict[str, Any])
async def create_resource_usage(
    usage_data: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource usage record for beta teacher."""
    try:
        service = BetaResourceManagementService(db, current_teacher.id)
        return await service.create_resource_usage(usage_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resource usage: {str(e)}"
        )


# ==================== RESOURCE THRESHOLDS ====================

@router.get("/thresholds", response_model=List[Dict[str, Any]])
async def get_resource_thresholds(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource thresholds for beta teacher."""
    try:
        service = BetaResourceManagementService(db, current_teacher.id)
        return await service.get_resource_thresholds(
            project_id=project_id,
            resource_type=resource_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resource thresholds: {str(e)}"
        )


@router.post("/thresholds", response_model=Dict[str, Any])
async def create_resource_threshold(
    threshold_data: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource threshold for beta teacher."""
    try:
        service = BetaResourceManagementService(db, current_teacher.id)
        return await service.create_resource_threshold(threshold_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resource threshold: {str(e)}"
        )


# ==================== RESOURCE OPTIMIZATIONS ====================

@router.get("/optimizations", response_model=List[Dict[str, Any]])
async def get_resource_optimizations(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, applied, rejected)"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource optimizations for beta teacher."""
    try:
        service = BetaResourceManagementService(db, current_teacher.id)
        return await service.get_resource_optimizations(
            project_id=project_id,
            status_filter=status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resource optimizations: {str(e)}"
        )


@router.post("/optimizations", response_model=Dict[str, Any])
async def create_resource_optimization(
    optimization_data: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource optimization for beta teacher."""
    try:
        service = BetaResourceManagementService(db, current_teacher.id)
        return await service.create_resource_optimization(optimization_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resource optimization: {str(e)}"
        )


# ==================== MIGRATION STATUS ====================

@router.get("/migration-status", response_model=Dict[str, int])
async def get_migration_status(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get migration status for beta teacher's resources."""
    try:
        service = BetaResourceManagementService(db, current_teacher.id)
        return await service.migrate_existing_resource_data()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving migration status: {str(e)}"
        )

