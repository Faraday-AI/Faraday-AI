"""
Dashboard API

This module provides the main API endpoints for the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dashboard.dependencies import get_current_user
from ....services.dashboard_service import DashboardService
from ....schemas.dashboard_schemas import (
    DashboardPreferences,
    DashboardState,
    DashboardInitResponse,
    GPTRecommendation,
    GPTSwitchResponse,
    DashboardMetrics,
    DashboardAnalytics,
    DashboardPerformance,
    DashboardIntegration,
    DashboardWidget
)

router = APIRouter()

@router.post("/initialize", response_model=DashboardInitResponse)
async def initialize_dashboard(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    preferences: Optional[DashboardPreferences] = None,
    include_metrics: bool = Query(True, description="Include initial metrics"),
    include_analytics: bool = Query(True, description="Include initial analytics"),
    include_performance: bool = Query(True, description="Include initial performance data")
):
    """Initialize dashboard for a new user."""
    service = DashboardService(db)
    result = await service.initialize_user_dashboard(
        user_id=current_user["id"],
        preferences=preferences.dict() if preferences else None
    )
    
    if include_metrics:
        result["metrics"] = await service.get_dashboard_metrics(current_user["id"])
    
    if include_analytics:
        result["analytics"] = await service.get_dashboard_analytics(current_user["id"])
    
    if include_performance:
        result["performance"] = await service.get_dashboard_performance(current_user["id"])
    
    return result

@router.get("/state", response_model=DashboardState)
async def get_dashboard_state(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_contexts: bool = Query(True, description="Include active contexts in response"),
    include_metrics: bool = Query(True, description="Include current metrics"),
    include_analytics: bool = Query(True, description="Include current analytics"),
    include_performance: bool = Query(True, description="Include current performance data"),
    include_collaboration: bool = Query(True, description="Include collaboration data")
):
    """Get current dashboard state."""
    service = DashboardService(db)
    result = await service.get_dashboard_state(
        user_id=current_user["id"],
        include_contexts=include_contexts
    )
    
    if include_metrics:
        result["metrics"] = await service.get_dashboard_metrics(current_user["id"])
    
    if include_analytics:
        result["analytics"] = await service.get_dashboard_analytics(current_user["id"])
    
    if include_performance:
        result["performance"] = await service.get_dashboard_performance(current_user["id"])
    
    if include_collaboration:
        result["collaboration"] = {
            "active_sessions": await service.get_collaboration_sessions(
                user_id=current_user["id"],
                status="active"
            ),
            "recent_documents": await service.get_collaboration_documents(
                user_id=current_user["id"]
            ),
            "metrics": await service.get_collaboration_metrics(
                user_id=current_user["id"]
            )
        }
    
    return result

@router.post("/gpts/switch", response_model=GPTSwitchResponse)
async def switch_primary_gpt(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    gpt_id: str = Query(..., description="ID of the GPT to switch to"),
    include_validation: bool = Query(True, description="Include validation results"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_metrics: bool = Query(True, description="Include switch metrics")
):
    """Switch primary GPT for the user."""
    service = DashboardService(db)
    result = await service.switch_primary_gpt(
        user_id=current_user["id"],
        gpt_id=gpt_id
    )
    
    if include_validation:
        result["validation"] = await service.validate_gpt_switch(
            user_id=current_user["id"],
            gpt_id=gpt_id
        )
    
    if include_impact:
        result["impact"] = await service.analyze_gpt_switch_impact(
            user_id=current_user["id"],
            gpt_id=gpt_id
        )
    
    if include_metrics:
        result["metrics"] = await service.get_gpt_switch_metrics(
            user_id=current_user["id"],
            gpt_id=gpt_id
        )
    
    return result

@router.put("/preferences", response_model=Dict)
async def update_preferences(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    preferences: DashboardPreferences,
    include_validation: bool = Query(True, description="Include validation results"),
    include_impact: bool = Query(True, description="Include impact analysis"),
    include_metrics: bool = Query(True, description="Include update metrics")
):
    """Update user dashboard preferences."""
    service = DashboardService(db)
    result = await service.update_dashboard_preferences(
        user_id=current_user["id"],
        preferences=preferences.dict()
    )
    
    if include_validation:
        result["validation"] = await service.validate_preferences_update(
            user_id=current_user["id"],
            preferences=preferences.dict()
        )
    
    if include_impact:
        result["impact"] = await service.analyze_preferences_impact(
            user_id=current_user["id"],
            preferences=preferences.dict()
        )
    
    if include_metrics:
        result["metrics"] = await service.get_preferences_update_metrics(
            user_id=current_user["id"],
            preferences=preferences.dict()
        )
    
    return result

@router.get("/gpts/recommendations", response_model=List[GPTRecommendation])
async def get_gpt_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    context_id: Optional[str] = Query(None, description="Optional context ID for recommendations"),
    include_metrics: bool = Query(True, description="Include recommendation metrics"),
    include_analytics: bool = Query(True, description="Include recommendation analytics"),
    include_performance: bool = Query(True, description="Include performance predictions")
):
    """Get GPT recommendations for the user."""
    service = DashboardService(db)
    result = await service.get_gpt_recommendations(
        user_id=current_user["id"],
        context_id=context_id
    )
    
    if include_metrics:
        result["metrics"] = await service.get_recommendation_metrics(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    if include_analytics:
        result["analytics"] = await service.get_recommendation_analytics(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    if include_performance:
        result["performance"] = await service.get_recommendation_performance(
            user_id=current_user["id"],
            context_id=context_id
        )
    
    return result

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_performance: bool = Query(True, description="Include performance metrics"),
    include_usage: bool = Query(True, description="Include usage metrics"),
    include_health: bool = Query(True, description="Include health metrics"),
    include_collaboration: bool = Query(True, description="Include collaboration metrics")
):
    """Get detailed dashboard metrics."""
    service = DashboardService(db)
    metrics = await service.get_dashboard_metrics(
        user_id=current_user["id"],
        include_performance=include_performance,
        include_usage=include_usage,
        include_health=include_health
    )
    
    if include_collaboration:
        metrics["collaboration_metrics"] = await service.get_collaboration_metrics(
            user_id=current_user["id"]
        )
    
    return metrics

@router.get("/analytics", response_model=DashboardAnalytics)
async def get_dashboard_analytics(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_trends: bool = Query(True, description="Include trend analysis"),
    include_patterns: bool = Query(True, description="Include usage patterns"),
    include_forecasts: bool = Query(True, description="Include usage forecasts"),
    include_collaboration: bool = Query(True, description="Include collaboration analytics")
):
    """Get detailed dashboard analytics."""
    service = DashboardService(db)
    analytics = await service.get_dashboard_analytics(
        user_id=current_user["id"],
        include_trends=include_trends,
        include_patterns=include_patterns,
        include_forecasts=include_forecasts
    )
    
    if include_collaboration:
        analytics["collaboration_analytics"] = await service.get_collaboration_analytics(
            user_id=current_user["id"]
        )
    
    return analytics

@router.get("/performance", response_model=DashboardPerformance)
async def get_dashboard_performance(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_benchmarks: bool = Query(True, description="Include performance benchmarks"),
    include_optimization: bool = Query(True, description="Include optimization opportunities"),
    include_recommendations: bool = Query(True, description="Include performance recommendations")
):
    """Get detailed dashboard performance data."""
    service = DashboardService(db)
    return await service.get_dashboard_performance(
        user_id=current_user["id"],
        include_benchmarks=include_benchmarks,
        include_optimization=include_optimization,
        include_recommendations=include_recommendations
    )

@router.get("/integrations", response_model=DashboardIntegration)
async def get_dashboard_integrations(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_status: bool = Query(True, description="Include integration status"),
    include_metrics: bool = Query(True, description="Include integration metrics"),
    include_recommendations: bool = Query(True, description="Include integration recommendations")
):
    """Get dashboard integrations."""
    service = DashboardService(db)
    result = await service.get_dashboard_integrations(
        user_id=current_user["id"]
    )
    
    if include_status:
        result["status"] = await service.get_integration_status(current_user["id"])
    
    if include_metrics:
        result["metrics"] = await service.get_integration_metrics(current_user["id"])
    
    if include_recommendations:
        result["recommendations"] = await service.get_integration_recommendations(current_user["id"])
    
    return result

@router.get("/layout")
async def get_dashboard_layout(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_widgets: bool = Query(True, description="Include widget configurations"),
    include_positions: bool = Query(True, description="Include widget positions"),
    include_sizes: bool = Query(True, description="Include widget sizes")
):
    """Get dashboard layout configuration."""
    service = DashboardService(db)
    return await service.get_dashboard_layout(
        user_id=current_user["id"],
        include_widgets=include_widgets,
        include_positions=include_positions,
        include_sizes=include_sizes
    )

@router.put("/layout")
async def update_dashboard_layout(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    layout: Dict,
    validate: bool = Query(True, description="Validate layout before updating")
):
    """Update dashboard layout configuration."""
    service = DashboardService(db)
    return await service.update_dashboard_layout(
        user_id=current_user["id"],
        layout=layout,
        validate=validate
    )

@router.get("/widgets", response_model=List[DashboardWidget])
async def get_dashboard_widgets(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    widget_type: Optional[str] = Query(None, description="Filter by widget type"),
    include_data: bool = Query(True, description="Include widget data"),
    include_config: bool = Query(True, description="Include widget configuration"),
    include_collaboration: bool = Query(True, description="Include collaboration widgets")
):
    """Get dashboard widgets."""
    service = DashboardService(db)
    widgets = await service.get_dashboard_widgets(
        user_id=current_user["id"],
        widget_type=widget_type,
        include_data=include_data,
        include_config=include_config
    )
    
    if include_collaboration:
        collaboration_widgets = await service.get_collaboration_widgets(
            user_id=current_user["id"]
        )
        for widget in widgets:
            if widget["type"] == "collaboration":
                widget.update(collaboration_widgets.get(widget["id"], {}))
    
    return widgets

@router.post("/widgets")
async def create_dashboard_widget(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    widget_type: str = Query(..., description="Type of widget to create"),
    configuration: Dict,
    position: Optional[Dict] = None,
    size: Optional[Dict] = None
):
    """Create a new dashboard widget."""
    service = DashboardService(db)
    return await service.create_dashboard_widget(
        user_id=current_user["id"],
        widget_type=widget_type,
        configuration=configuration,
        position=position,
        size=size
    )

@router.put("/widgets/{widget_id}")
async def update_dashboard_widget(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    widget_id: str,
    configuration: Optional[Dict] = None,
    position: Optional[Dict] = None,
    size: Optional[Dict] = None
):
    """Update a dashboard widget."""
    service = DashboardService(db)
    return await service.update_dashboard_widget(
        user_id=current_user["id"],
        widget_id=widget_id,
        configuration=configuration,
        position=position,
        size=size
    )

@router.delete("/widgets/{widget_id}")
async def delete_dashboard_widget(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    widget_id: str
):
    """Delete a dashboard widget."""
    service = DashboardService(db)
    return await service.delete_dashboard_widget(
        user_id=current_user["id"],
        widget_id=widget_id
    )

@router.get("/themes")
async def get_dashboard_themes(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    include_custom: bool = Query(True, description="Include custom themes"),
    include_preview: bool = Query(True, description="Include theme previews")
):
    """Get available dashboard themes."""
    service = DashboardService(db)
    return await service.get_dashboard_themes(
        user_id=current_user["id"],
        include_custom=include_custom,
        include_preview=include_preview
    )

@router.post("/themes")
async def create_dashboard_theme(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    theme: Dict
):
    """Create a custom dashboard theme."""
    service = DashboardService(db)
    return await service.create_dashboard_theme(
        user_id=current_user["id"],
        theme=theme
    )

@router.put("/themes/{theme_id}")
async def update_dashboard_theme(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    theme_id: str,
    theme: Dict
):
    """Update a custom dashboard theme."""
    service = DashboardService(db)
    return await service.update_dashboard_theme(
        user_id=current_user["id"],
        theme_id=theme_id,
        theme=theme
    )

@router.delete("/themes/{theme_id}")
async def delete_dashboard_theme(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    theme_id: str
):
    """Delete a custom dashboard theme."""
    service = DashboardService(db)
    return await service.delete_dashboard_theme(
        user_id=current_user["id"],
        theme_id=theme_id
    )

@router.post("/export")
async def export_dashboard(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    format: str = Query(..., regex="^(json|csv|pdf)$"),
    include_data: bool = Query(True, description="Include dashboard data"),
    include_config: bool = Query(True, description="Include dashboard configuration"),
    time_range: Optional[str] = Query(None, regex="^(24h|7d|30d)$")
):
    """Export dashboard data and configuration."""
    service = DashboardService(db)
    return await service.export_dashboard(
        user_id=current_user["id"],
        format=format,
        include_data=include_data,
        include_config=include_config,
        time_range=time_range
    )

@router.post("/share")
async def share_dashboard(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    share_type: str = Query(..., regex="^(link|embed|export)$"),
    expiration: Optional[int] = Query(None, description="Expiration time in hours"),
    permissions: Optional[Dict] = None
):
    """Share dashboard with others."""
    service = DashboardService(db)
    return await service.share_dashboard(
        user_id=current_user["id"],
        share_type=share_type,
        expiration=expiration,
        permissions=permissions
    )

@router.get("/search")
async def search_dashboard(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    query: str = Query(..., description="Search query"),
    filters: Optional[Dict] = None,
    include_widgets: bool = Query(True, description="Include widgets in search"),
    include_data: bool = Query(True, description="Include dashboard data in search")
):
    """Search dashboard content."""
    service = DashboardService(db)
    return await service.search_dashboard(
        user_id=current_user["id"],
        query=query,
        filters=filters,
        include_widgets=include_widgets,
        include_data=include_data
    )

@router.get("/filters")
async def get_dashboard_filters(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    filter_type: Optional[str] = Query(None, description="Filter by type"),
    include_values: bool = Query(True, description="Include filter values"),
    include_usage: bool = Query(True, description="Include filter usage stats")
):
    """Get available dashboard filters."""
    service = DashboardService(db)
    return await service.get_dashboard_filters(
        user_id=current_user["id"],
        filter_type=filter_type,
        include_values=include_values,
        include_usage=include_usage
    )

@router.post("/filters")
async def create_dashboard_filter(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    filter_type: str = Query(..., description="Type of filter to create"),
    configuration: Dict,
    apply_to: Optional[List[str]] = Query(None, description="Widget IDs to apply filter to")
):
    """Create a new dashboard filter."""
    service = DashboardService(db)
    return await service.create_dashboard_filter(
        user_id=current_user["id"],
        filter_type=filter_type,
        configuration=configuration,
        apply_to=apply_to
    )

@router.put("/filters/{filter_id}")
async def update_dashboard_filter(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    filter_id: str,
    configuration: Dict,
    apply_to: Optional[List[str]] = Query(None, description="Widget IDs to apply filter to")
):
    """Update a dashboard filter."""
    service = DashboardService(db)
    return await service.update_dashboard_filter(
        user_id=current_user["id"],
        filter_id=filter_id,
        configuration=configuration,
        apply_to=apply_to
    )

@router.delete("/filters/{filter_id}")
async def delete_dashboard_filter(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    filter_id: str
):
    """Delete a dashboard filter."""
    service = DashboardService(db)
    return await service.delete_dashboard_filter(
        user_id=current_user["id"],
        filter_id=filter_id
    ) 