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

@router.get("/metrics/{org_id}", response_model=OptimizationMetricsResponse, response_model_exclude_none=True)
async def get_optimization_metrics(
    org_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_anomalies: bool = Query(True, description="Include anomaly detection"),
    include_recommendations: bool = Query(True, description="Include optimization recommendations"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Get real-time optimization metrics.
    
    Args:
        org_id: Organization ID
        time_range: Time range for analysis (24h, 7d, 30d)
        include_anomalies: Whether to include anomaly detection
        include_recommendations: Whether to include optimization recommendations
    """
    # Note: OAuth2 dependency should handle auth - if we get here, auth passed
    # No need for additional checks as oauth2_scheme raises 401 for unauthorized requests
    try:
        # Create service instance
        service = OptimizationMonitoringService(db)
        
        # Call service method - will raise if there's an error
        metrics = await service.get_optimization_metrics(
            org_id=org_id,
            time_range=time_range
        )

        # Remove fields if not requested (ensure complete removal)
        # Build a new dict without unwanted keys, and explicitly set None values to be excluded
        result = {}
        for key, value in metrics.items():
            if key == "anomalies":
                if include_anomalies:
                    result[key] = value
                # Skip if not included
            elif key == "recommendations":
                if include_recommendations:
                    result[key] = value
                # Skip if not included
            else:
                result[key] = value
        
        # Return dict directly - FastAPI response_model will validate but won't add excluded keys
        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting optimization metrics: {str(e)}"
        )

@router.get("/insights/{org_id}", response_model=OptimizationInsightsResponse, response_model_exclude_none=True)
async def get_optimization_insights(
    org_id: str,
    time_range: str = Query("24h", regex="^(24h|7d|30d)$"),
    include_patterns: bool = Query(True, description="Include pattern analysis"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    include_opportunities: bool = Query(True, description="Include optimization opportunities"),
    include_risks: bool = Query(True, description="Include risk assessment"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
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
    # Note: OAuth2 dependency should handle auth - if we get here, auth passed
    # The get_current_user dependency will raise 401 if oauth2_scheme fails
    
    try:
        # Create service instance
        service = OptimizationMonitoringService(db)
        
        # Call service method - will raise if there's an error
        insights = await service.get_optimization_insights(
            org_id=org_id,
            time_range=time_range
        )

        # Remove fields if not requested (ensure complete removal)
        # Build a new dict without unwanted keys, and explicitly set None values to be excluded
        result = {}
        for key, value in insights.items():
            if key == "patterns":
                if include_patterns:
                    result[key] = value
            elif key == "trends":
                if include_trends:
                    result[key] = value
            elif key == "opportunities":
                if include_opportunities:
                    result[key] = value
            elif key == "risks":
                if include_risks:
                    result[key] = value
            else:
                result[key] = value
        
        # Return dict directly - FastAPI response_model will validate but won't add excluded keys
        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting optimization insights: {str(e)}"
        ) 