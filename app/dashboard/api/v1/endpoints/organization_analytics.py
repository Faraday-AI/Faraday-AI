"""
Organization Analytics API Endpoints

This module provides the API endpoints for organization analytics and reporting
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....dependencies import get_db, get_current_user
from ....services.organization_analytics_service import OrganizationAnalyticsService
from ....schemas.analytics import (
    OrganizationMetricsResponse,
    CollaborationAnalyticsResponse,
    ResourceAnalyticsResponse,
    PerformanceReportResponse
)

router = APIRouter()

@router.get("/organizations/{org_id}/metrics", response_model=OrganizationMetricsResponse)
async def get_organization_metrics(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for metrics (e.g., 24h, 7d, 30d)")
):
    """Get comprehensive organization metrics."""
    analytics_service = OrganizationAnalyticsService(db)
    return await analytics_service.get_organization_metrics(
        org_id=org_id,
        time_range=time_range
    )

@router.get("/organizations/{org_id}/collaboration-analytics", response_model=CollaborationAnalyticsResponse)
async def get_collaboration_analytics(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for analytics (e.g., 24h, 7d, 30d)")
):
    """Get detailed collaboration analytics."""
    analytics_service = OrganizationAnalyticsService(db)
    return await analytics_service.get_collaboration_analytics(
        org_id=org_id,
        time_range=time_range
    )

@router.get("/organizations/{org_id}/resource-analytics", response_model=ResourceAnalyticsResponse)
async def get_resource_analytics(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for analytics (e.g., 24h, 7d, 30d)")
):
    """Get detailed resource usage analytics."""
    analytics_service = OrganizationAnalyticsService(db)
    return await analytics_service.get_resource_analytics(
        org_id=org_id,
        time_range=time_range
    )

@router.get("/organizations/{org_id}/performance-report", response_model=PerformanceReportResponse)
async def get_performance_report(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for report (e.g., 24h, 7d, 30d)"),
    include_predictions: bool = Query(True, description="Include performance predictions")
):
    """Generate comprehensive performance report."""
    analytics_service = OrganizationAnalyticsService(db)
    return await analytics_service.get_performance_report(
        org_id=org_id,
        time_range=time_range,
        include_predictions=include_predictions
    ) 