"""
Optimization Monitoring API endpoints for the Faraday AI Dashboard.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....services.optimization_monitoring_service import OptimizationMonitoringService
from ....dependencies import get_db, get_current_user
from ....schemas.optimization_monitoring import (
    OptimizationMetricsResponse,
    OptimizationInsightsResponse
)

router = APIRouter()

@router.get("/metrics/{org_id}", response_model=OptimizationMetricsResponse)
async def get_optimization_metrics(
    org_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_anomalies: bool = Query(True, description="Include anomaly detection"),
    include_recommendations: bool = Query(True, description="Include optimization recommendations"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get real-time optimization metrics.
    
    Args:
        org_id: Organization ID
        time_range: Time range for analysis (24h, 7d, 30d)
        include_anomalies: Whether to include anomaly detection
        include_recommendations: Whether to include optimization recommendations
    """
    try:
        service = OptimizationMonitoringService(db)
        metrics = await service.get_optimization_metrics(
            org_id=org_id,
            time_range=time_range
        )

        if not include_anomalies:
            metrics.pop("anomalies", None)
        if not include_recommendations:
            metrics.pop("recommendations", None)

        return metrics

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting optimization metrics: {str(e)}"
        )

@router.get("/insights/{org_id}", response_model=OptimizationInsightsResponse)
async def get_optimization_insights(
    org_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_patterns: bool = Query(True, description="Include pattern analysis"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    include_opportunities: bool = Query(True, description="Include optimization opportunities"),
    include_risks: bool = Query(True, description="Include risk assessment"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get AI-driven optimization insights.
    
    Args:
        org_id: Organization ID
        time_range: Time range for analysis (24h, 7d, 30d)
        include_patterns: Whether to include pattern analysis
        include_trends: Whether to include trend analysis
        include_opportunities: Whether to include optimization opportunities
        include_risks: Whether to include risk assessment
    """
    try:
        service = OptimizationMonitoringService(db)
        insights = await service.get_optimization_insights(
            org_id=org_id,
            time_range=time_range
        )

        if not include_patterns:
            insights.pop("patterns", None)
        if not include_trends:
            insights.pop("trends", None)
        if not include_opportunities:
            insights.pop("opportunities", None)
        if not include_risks:
            insights.pop("risks", None)

        return insights

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting optimization insights: {str(e)}"
        ) 