"""
FastAPI endpoints for Beta Teacher Dashboard
Provides REST API for dashboard configuration, widgets, and analytics for the beta teacher system
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.beta_teacher_dashboard_service import BetaTeacherDashboardService
from app.schemas.beta_teacher_dashboard import (
    DashboardConfigResponse,
    BetaDashboardWidgetResponse,
    DashboardAnalyticsResponse,
    DashboardFeedbackResponse,
    BetaDashboardWidgetConfigUpdate,
    DashboardLayoutUpdate,
    DashboardPreferencesUpdate
)
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration

router = APIRouter(prefix="/beta/dashboard", tags=["Beta Teacher Dashboard"])


# ==================== DASHBOARD CONFIGURATION ====================

@router.get("", response_model=DashboardConfigResponse)
async def get_dashboard(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the teacher's dashboard configuration"""
    try:
        service = BetaTeacherDashboardService(db)
        return service.get_dashboard(current_teacher.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dashboard not found: {str(e)}"
        )


@router.put("", response_model=DashboardConfigResponse)
async def update_dashboard(
    update_data: DashboardLayoutUpdate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the teacher's dashboard configuration"""
    try:
        service = BetaTeacherDashboardService(db)
        return service.update_dashboard(current_teacher.id, update_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update dashboard: {str(e)}"
        )


# ==================== DASHBOARD WIDGETS ====================

@router.get("/widgets", response_model=List[BetaDashboardWidgetResponse])
async def get_dashboard_widgets(
    widget_type: Optional[str] = Query(None, description="Filter by widget type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=500, description="Number of widgets to return"),
    offset: int = Query(0, ge=0, description="Number of widgets to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard widgets for the teacher"""
    service = BetaTeacherDashboardService(db)
    return service.get_dashboard_widgets(current_teacher.id, widget_type, is_active, limit, offset)


@router.get("/widgets/{widget_id}", response_model=BetaDashboardWidgetResponse)
async def get_dashboard_widget(
    widget_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific dashboard widget"""
    service = BetaTeacherDashboardService(db)
    widget = service.get_dashboard_widget(widget_id, current_teacher.id)
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or access denied"
        )
    
    return widget


@router.put("/widgets/{widget_id}", response_model=BetaDashboardWidgetResponse)
async def update_dashboard_widget(
    widget_id: str,
    update_data: BetaDashboardWidgetConfigUpdate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a dashboard widget configuration"""
    service = BetaTeacherDashboardService(db)
    widget = service.update_dashboard_widget(widget_id, current_teacher.id, update_data)
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or access denied"
        )
    
    return widget


@router.post("/widgets/{widget_id}/activate", response_model=BetaDashboardWidgetResponse)
async def activate_widget(
    widget_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a dashboard widget"""
    service = BetaTeacherDashboardService(db)
    widget = service.activate_widget(widget_id, current_teacher.id)
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or access denied"
        )
    
    return widget


@router.post("/widgets/{widget_id}/deactivate", response_model=BetaDashboardWidgetResponse)
async def deactivate_widget(
    widget_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a dashboard widget"""
    service = BetaTeacherDashboardService(db)
    widget = service.deactivate_widget(widget_id, current_teacher.id)
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or access denied"
        )
    
    return widget


# ==================== DASHBOARD ANALYTICS ====================

@router.get("/analytics", response_model=DashboardAnalyticsResponse)
async def get_dashboard_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics for the teacher"""
    service = BetaTeacherDashboardService(db)
    return service.get_dashboard_analytics(current_teacher.id, days)


@router.get("/analytics/widgets", response_model=Dict[str, Any])
async def get_widget_analytics(
    widget_id: Optional[str] = Query(None, description="Filter by widget ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for specific widgets"""
    service = BetaTeacherDashboardService(db)
    return service.get_widget_analytics(current_teacher.id, widget_id, days)


# ==================== DASHBOARD FEEDBACK ====================

@router.post("/feedback", response_model=DashboardFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_dashboard_feedback(
    feedback_data: Dict[str, Any],
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback about the dashboard"""
    try:
        service = BetaTeacherDashboardService(db)
        return service.submit_dashboard_feedback(current_teacher.id, feedback_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/feedback", response_model=List[DashboardFeedbackResponse])
async def get_dashboard_feedback(
    feedback_type: Optional[str] = Query(None, description="Filter by feedback type"),
    limit: int = Query(50, ge=1, le=100, description="Number of feedback items to return"),
    offset: int = Query(0, ge=0, description="Number of feedback items to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard feedback for the teacher"""
    service = BetaTeacherDashboardService(db)
    return service.get_dashboard_feedback(current_teacher.id, feedback_type, limit, offset)


# ==================== DASHBOARD PREFERENCES ====================

@router.get("/preferences", response_model=Dict[str, Any])
async def get_dashboard_preferences(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard preferences for the teacher"""
    service = BetaTeacherDashboardService(db)
    return service.get_dashboard_preferences(current_teacher.id)


@router.put("/preferences", response_model=Dict[str, Any])
async def update_dashboard_preferences(
    update_data: DashboardPreferencesUpdate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update dashboard preferences for the teacher"""
    service = BetaTeacherDashboardService(db)
    return service.update_dashboard_preferences(current_teacher.id, update_data)


# ==================== BETA WIDGETS ====================

@router.get("/beta/widgets", response_model=List[BetaDashboardWidgetResponse])
async def get_beta_widgets(
    widget_type: Optional[str] = Query(None, description="Filter by widget type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(330, ge=1, le=500, description="Number of widgets to return"),
    offset: int = Query(0, ge=0, description="Number of widgets to skip"),
    db: Session = Depends(get_db)
):
    """Get all available beta widgets"""
    service = BetaTeacherDashboardService(db)
    return service.get_beta_widgets(widget_type, is_active, limit, offset)


# ==================== DASHBOARD RESET ====================

@router.post("/reset", response_model=DashboardConfigResponse)
async def reset_dashboard(
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset the dashboard to default configuration"""
    try:
        service = BetaTeacherDashboardService(db)
        return service.reset_dashboard(current_teacher.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reset dashboard: {str(e)}"
        )


# ==================== HEALTH CHECK ====================

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for teacher dashboard"""
    return {
        "status": "healthy",
        "service": "beta-teacher-dashboard",
        "version": "1.0.0"
    }

