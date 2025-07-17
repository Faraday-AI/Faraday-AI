from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....dependencies import get_db, get_current_user
from ....services.dashboard_service import DashboardService
from ....schemas.resource_sharing import (
    ResourceUsageResponse,
    ResourceOptimizationResponse,
    ResourcePredictionResponse,
    CrossOrgPatternsResponse,
    SecurityMetricsResponse,
    ResourceSharingWidgetCreate,
    ResourceSharingWidgetUpdate,
    ResourceSharingWidgetResponse
)

router = APIRouter()

@router.post("/widgets/resource-sharing", response_model=ResourceSharingWidgetResponse)
async def create_resource_sharing_widget(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    widget: ResourceSharingWidgetCreate
):
    """Create a new resource sharing widget."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service.create_dashboard_widget(
            user_id=current_user["id"],
            widget_type=widget.widget_type,
            configuration=widget.configuration.dict(),
            position=widget.position,
            size=widget.size
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create resource sharing widget: {str(e)}"
        )

@router.get("/widgets/resource-sharing/{widget_id}", response_model=ResourceSharingWidgetResponse)
async def get_resource_sharing_widget(
    widget_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific resource sharing widget."""
    try:
        dashboard_service = DashboardService(db)
        widgets = await dashboard_service.get_dashboard_widgets(
            user_id=current_user["id"],
            widget_type=None,
            include_data=True
        )
        widget = next((w for w in widgets if w["id"] == widget_id), None)
        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")
        return widget
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource sharing widget: {str(e)}"
        )

@router.put("/widgets/resource-sharing/{widget_id}", response_model=ResourceSharingWidgetResponse)
async def update_resource_sharing_widget(
    widget_id: str,
    widget: ResourceSharingWidgetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a resource sharing widget."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service.update_dashboard_widget(
            user_id=current_user["id"],
            widget_id=widget_id,
            configuration=widget.configuration.dict() if widget.configuration else None,
            position=widget.position,
            size=widget.size
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update resource sharing widget: {str(e)}"
        )

@router.delete("/widgets/resource-sharing/{widget_id}")
async def delete_resource_sharing_widget(
    widget_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a resource sharing widget."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service.delete_dashboard_widget(
            user_id=current_user["id"],
            widget_id=widget_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete resource sharing widget: {str(e)}"
        )

@router.get("/resource-usage/{org_id}", response_model=ResourceUsageResponse)
async def get_resource_usage(
    org_id: str,
    time_range: str = Query("24h", description="Time range for metrics (e.g., '24h', '7d', '30d')"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get resource usage metrics for an organization."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service._get_resource_usage_data({
            "organization_id": org_id,
            "time_range": time_range
        })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource usage data: {str(e)}"
        )

@router.get("/resource-optimization/{org_id}", response_model=ResourceOptimizationResponse)
async def get_resource_optimization(
    org_id: str,
    resource_type: str = Query(..., description="Type of resource to optimize"),
    time_range: str = Query("24h", description="Time range for analysis"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get resource optimization recommendations."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service._get_resource_optimization_data({
            "organization_id": org_id,
            "resource_type": resource_type,
            "time_range": time_range
        })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource optimization data: {str(e)}"
        )

@router.get("/resource-prediction/{org_id}", response_model=ResourcePredictionResponse)
async def get_resource_prediction(
    org_id: str,
    resource_type: str = Query(..., description="Type of resource to predict"),
    prediction_window: str = Query("7d", description="Prediction window (e.g., '7d', '30d')"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get resource usage predictions."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service._get_resource_prediction_data({
            "organization_id": org_id,
            "resource_type": resource_type,
            "prediction_window": prediction_window
        })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get resource prediction data: {str(e)}"
        )

@router.get("/cross-org-patterns/{org_id}", response_model=CrossOrgPatternsResponse)
async def get_cross_org_patterns(
    org_id: str,
    time_range: str = Query("30d", description="Time range for pattern analysis"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get cross-organization sharing patterns."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service._get_cross_org_patterns_data({
            "organization_id": org_id,
            "time_range": time_range
        })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cross-organization patterns: {str(e)}"
        )

@router.get("/security-metrics/{org_id}", response_model=SecurityMetricsResponse)
async def get_security_metrics(
    org_id: str,
    resource_type: str = Query(..., description="Type of resource for security analysis"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get security metrics for resource sharing."""
    try:
        dashboard_service = DashboardService(db)
        result = await dashboard_service._get_security_metrics_data({
            "organization_id": org_id,
            "resource_type": resource_type
        })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get security metrics: {str(e)}"
        ) 