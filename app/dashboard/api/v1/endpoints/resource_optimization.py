"""
Resource Optimization API Endpoints

This module provides API endpoints for resource optimization features
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from enum import Enum
import re

from ....dependencies import get_db, get_current_user
from ....services.smart_sharing_patterns_service import SmartSharingPatternsService
from ....services.predictive_access_service import PredictiveAccessService
from ....services.cross_org_optimization_service import CrossOrgOptimizationService
from ....services.resource_optimization_service import ResourceOptimizationService
from ....schemas.resource_sharing_optimization import (
    SharingPatternResponse,
    AccessPredictionResponse,
    SecurityRiskResponse,
    SharingScheduleResponse,
    CrossOrgOptimizationResponse
)

router = APIRouter()

# Optimization target enum
class OptimizationTarget(str, Enum):
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"

def validate_time_window(time_window: str) -> str:
    """Validate time window format."""
    if not re.match(r'^\d+[hdwmy]$', time_window):
        raise HTTPException(
            status_code=422,
            detail="Invalid time window format. Use format like '24h', '7d', '1w', '1m', '1y'"
        )
    return time_window

def validate_forecast_window(forecast_window: str) -> str:
    """Validate forecast window format."""
    if not re.match(r'^\d+[hdwmy]$', forecast_window):
        raise HTTPException(
            status_code=422,
            detail="Invalid forecast window format. Use format like '24h', '7d', '1w', '1m', '1y'"
        )
    return forecast_window

def validate_gpt_id(gpt_id: str) -> str:
    """Validate GPT ID format."""
    if not re.match(r'^[a-zA-Z0-9_-]+$', gpt_id) or len(gpt_id) < 3:
        raise HTTPException(
            status_code=422,
            detail="Invalid GPT ID format. Must be alphanumeric with hyphens/underscores and at least 3 characters"
        )
    return gpt_id

# Resource optimization endpoints (for tests)
@router.get("/optimize/{gpt_id}")
async def optimize_resources(
    gpt_id: str,
    optimization_target: OptimizationTarget = Query(OptimizationTarget.BALANCED, description="Optimization target"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Optimize resources for a specific GPT."""
    try:
        # Validate GPT ID
        validate_gpt_id(gpt_id)
        
        service = ResourceOptimizationService(db)
        result = await service.optimize_resources(gpt_id, optimization_target.value)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/allocation-plan")
async def get_resource_allocation_plan(
    time_window: str = Query("24h", description="Time window for analysis"),
    category: Optional[str] = Query(None, description="GPT category filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get resource allocation plan."""
    try:
        # Validate time window
        validate_time_window(time_window)
        
        service = ResourceOptimizationService(db)
        result = await service.get_resource_allocation_plan(time_window, category)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scaling/{gpt_id}")
async def get_scaling_recommendations(
    gpt_id: str,
    forecast_window: str = Query("7d", description="Forecast window"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get scaling recommendations for a specific GPT."""
    try:
        # Validate GPT ID
        validate_gpt_id(gpt_id)
        # Validate forecast window
        validate_forecast_window(forecast_window)
        
        service = ResourceOptimizationService(db)
        result = await service.get_scaling_recommendations(gpt_id, forecast_window)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_optimization_dashboard(
    time_window: str = Query("24h", description="Time window for analysis"),
    category: Optional[str] = Query(None, description="GPT category filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get optimization dashboard data."""
    try:
        # Validate time window
        validate_time_window(time_window)
        
        service = ResourceOptimizationService(db)
        result = await service.get_optimization_dashboard(time_window, category)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Smart Resource Sharing Patterns endpoints
@router.get(
    "/organizations/{org_id}/sharing-patterns",
    response_model=SharingPatternResponse,
    tags=["Resource Optimization"]
)
async def analyze_sharing_patterns(
    org_id: str,
    time_range: str = Query("30d", description="Time range for analysis (e.g., 30d, 7d)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze resource sharing patterns for an organization.
    
    This endpoint provides:
    - Pattern identification across resource types and access levels
    - Success metrics calculation
    - Optimal configuration identification
    - Pattern-based recommendations
    """
    patterns_service = SmartSharingPatternsService(db)
    return await patterns_service.analyze_sharing_patterns(org_id, time_range)

@router.get(
    "/organizations/{org_id}/collaboration-opportunities",
    response_model=List[Dict[str, Any]],
    tags=["Resource Optimization"]
)
async def predict_collaboration_opportunities(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Predict potential collaboration opportunities with other organizations.
    
    This endpoint identifies:
    - Organizations with complementary resource profiles
    - Potential collaboration benefits
    - Recommended collaboration strategies
    """
    patterns_service = SmartSharingPatternsService(db)
    return await patterns_service.predict_collaboration_opportunities(org_id)

# Predictive Access Management endpoints
@router.get(
    "/organizations/{org_id}/resources/{resource_id}/access-predictions",
    response_model=AccessPredictionResponse,
    tags=["Resource Optimization"]
)
async def predict_access_needs(
    org_id: str,
    resource_id: str,
    prediction_window: str = Query("7d", description="Prediction window (e.g., 7d, 30d)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Predict future access level needs for a resource.
    
    This endpoint provides:
    - Access level predictions
    - Usage trend analysis
    - Confidence scores
    - Access recommendations
    """
    access_service = PredictiveAccessService(db)
    return await access_service.predict_access_needs(
        org_id,
        resource_id,
        prediction_window
    )

@router.get(
    "/organizations/{org_id}/security-risks",
    response_model=SecurityRiskResponse,
    tags=["Resource Optimization"]
)
async def detect_security_risks(
    org_id: str,
    time_range: str = Query("24h", description="Time range for risk detection (e.g., 24h, 7d)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Detect potential security risks in resource sharing.
    
    This endpoint identifies:
    - Access pattern anomalies
    - Security risk factors
    - Risk assessments
    - Mitigation suggestions
    """
    access_service = PredictiveAccessService(db)
    return await access_service.detect_security_risks(org_id, time_range)

@router.get(
    "/organizations/{org_id}/access-optimization",
    response_model=List[Dict[str, Any]],
    tags=["Resource Optimization"]
)
async def get_access_optimization_suggestions(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get suggestions for optimizing access levels.
    
    This endpoint provides:
    - Access level optimization suggestions
    - Usage pattern analysis
    - Efficiency recommendations
    """
    access_service = PredictiveAccessService(db)
    return await access_service.get_access_optimization_suggestions(org_id)

# Cross-Organization Resource Optimization endpoints
@router.get(
    "/organizations/{org_id}/sharing-efficiency",
    response_model=CrossOrgOptimizationResponse,
    tags=["Resource Optimization"]
)
async def analyze_sharing_efficiency(
    org_id: str,
    time_range: str = Query("30d", description="Time range for analysis (e.g., 30d, 7d)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze resource sharing efficiency across organizations.
    
    This endpoint provides:
    - Efficiency metrics calculation
    - Optimization opportunity identification
    - Efficiency recommendations
    """
    optimization_service = CrossOrgOptimizationService(db)
    return await optimization_service.analyze_sharing_efficiency(org_id, time_range)

@router.get(
    "/organizations/{org_id}/sharing-schedule",
    response_model=SharingScheduleResponse,
    tags=["Resource Optimization"]
)
async def suggest_sharing_schedule(
    org_id: str,
    resource_type: Optional[str] = Query(None, description="Optional resource type filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Suggest optimal sharing schedule based on usage patterns.
    
    This endpoint provides:
    - Optimal sharing windows
    - Peak/off-peak hours identification
    - Schedule impact analysis
    - Implementation plan
    """
    optimization_service = CrossOrgOptimizationService(db)
    return await optimization_service.suggest_sharing_schedule(org_id, resource_type)

@router.get(
    "/organizations/{org_id}/complementary-patterns",
    response_model=List[Dict[str, Any]],
    tags=["Resource Optimization"]
)
async def find_complementary_patterns(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Find complementary resource usage patterns across organizations.
    
    This endpoint identifies:
    - Complementary usage patterns
    - Collaboration opportunities
    - Resource sharing suggestions
    """
    optimization_service = CrossOrgOptimizationService(db)
    return await optimization_service.find_complementary_patterns(org_id) 