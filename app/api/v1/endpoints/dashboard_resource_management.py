"""
FastAPI endpoints for Dashboard Resource Management Service
Provides REST API for resource management in the main system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dashboard.services.resource_management_service import ResourceManagementService
from app.core.auth import get_current_user
from app.models.core.user import User

router = APIRouter(prefix="/dashboard/resources", tags=["Dashboard Resource Management"])

# Export router for use in main app
__all__ = ['router']


# ==================== RESOURCE USAGE ====================

@router.get("/usage", response_model=List[Dict[str, Any]])
async def get_resource_usage(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource usage records."""
    try:
        service = ResourceManagementService(db)
        return await service.get_resource_usage(
            user_id=user_id,
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource usage record."""
    try:
        service = ResourceManagementService(db)
        # Set user_id from current user if not provided
        if 'user_id' not in usage_data:
            usage_data['user_id'] = current_user.id
        return await service.create_resource_usage(usage_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resource usage: {str(e)}"
        )


# ==================== RESOURCE THRESHOLDS ====================

@router.get("/thresholds", response_model=List[Dict[str, Any]])
async def get_resource_thresholds(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource thresholds."""
    try:
        service = ResourceManagementService(db)
        return await service.get_resource_thresholds(
            user_id=user_id,
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource threshold."""
    try:
        service = ResourceManagementService(db)
        # Set user_id from current user if not provided
        if 'user_id' not in threshold_data:
            threshold_data['user_id'] = current_user.id
        return await service.create_resource_threshold(threshold_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resource threshold: {str(e)}"
        )


# ==================== RESOURCE OPTIMIZATIONS ====================

@router.get("/optimizations", response_model=List[Dict[str, Any]])
async def get_resource_optimizations(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, applied, rejected)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource optimizations."""
    try:
        service = ResourceManagementService(db)
        return await service.get_resource_optimizations(
            user_id=user_id,
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource optimization."""
    try:
        service = ResourceManagementService(db)
        # Set user_id from current user if not provided
        if 'user_id' not in optimization_data:
            optimization_data['user_id'] = current_user.id
        return await service.create_resource_optimization(optimization_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating resource optimization: {str(e)}"
        )


# ==================== MIGRATION STATUS ====================

@router.get("/migration-status", response_model=Dict[str, int])
async def get_migration_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get migration status for resource data."""
    try:
        service = ResourceManagementService(db)
        return await service.migrate_existing_resource_data()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving migration status: {str(e)}"
        )

