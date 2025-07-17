"""
Resource Optimization Schemas

This module provides Pydantic models for resource optimization-related data validation
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ResourceMetrics(BaseModel):
    """Resource metrics schema."""
    id: str = Field(..., description="Resource ID")
    type: str = Field(..., description="Resource type")
    status: str = Field(..., description="Resource status")
    utilization: float = Field(..., description="Resource utilization rate")
    efficiency: float = Field(..., description="Resource efficiency score")
    cost: Dict[str, float] = Field(..., description="Resource cost metrics")
    performance: Dict[str, Any] = Field(..., description="Resource performance metrics")

class OptimizationRecommendation(BaseModel):
    """Optimization recommendation schema."""
    id: str = Field(..., description="Recommendation ID")
    type: str = Field(..., description="Recommendation type")
    action: str = Field(..., description="Recommended action")
    priority: int = Field(..., description="Priority level (1-10)")
    impact: float = Field(..., description="Expected impact score")
    estimated_savings: Optional[float] = Field(None, description="Estimated cost savings")
    estimated_improvement: Optional[float] = Field(None, description="Estimated performance improvement")
    estimated_efficiency_gain: Optional[float] = Field(None, description="Estimated efficiency gain")
    complexity: int = Field(..., description="Implementation complexity (1-10)")
    dependencies: List[str] = Field(default=[], description="Dependent recommendation IDs")
    risks: List[Dict[str, Any]] = Field(default=[], description="Associated risks")
    description: str = Field(..., description="Detailed description")
    implementation_steps: List[str] = Field(..., description="Implementation steps")

class OptimizationImpact(BaseModel):
    """Optimization impact schema."""
    cost_savings: float = Field(..., description="Total cost savings")
    performance_improvement: float = Field(..., description="Overall performance improvement")
    efficiency_gain: float = Field(..., description="Overall efficiency gain")
    resource_reduction: float = Field(..., description="Resource reduction count")
    bottleneck_reduction: int = Field(..., description="Bottleneck reduction count")
    risks: List[Dict[str, Any]] = Field(..., description="Potential risks")

class ImplementationPhase(BaseModel):
    """Implementation phase schema."""
    recommendations: List[OptimizationRecommendation] = Field(..., description="Phase recommendations")
    start_date: datetime = Field(..., description="Phase start date")
    end_date: datetime = Field(..., description="Phase end date")
    duration: str = Field(..., description="Phase duration")

class ImplementationPlan(BaseModel):
    """Implementation plan schema."""
    phases: Dict[str, List[OptimizationRecommendation]] = Field(..., description="Implementation phases")
    timeline: Dict[str, Dict[str, Any]] = Field(..., description="Phase timeline")
    dependencies: List[Dict[str, Any]] = Field(..., description="Phase dependencies")
    risks: List[Dict[str, Any]] = Field(..., description="Implementation risks")

class OptimizationResponse(BaseModel):
    """Optimization response schema."""
    current_state: Dict[str, Any] = Field(..., description="Current resource state")
    recommendations: List[OptimizationRecommendation] = Field(..., description="Optimization recommendations")
    impact: OptimizationImpact = Field(..., description="Optimization impact")
    implementation_plan: ImplementationPlan = Field(..., description="Implementation plan")

class OptimizationHistoryEntry(BaseModel):
    """Optimization history entry schema."""
    id: str = Field(..., description="History entry ID")
    timestamp: datetime = Field(..., description="Optimization timestamp")
    optimization_type: str = Field(..., description="Type of optimization")
    recommendations: List[OptimizationRecommendation] = Field(..., description="Applied recommendations")
    impact: OptimizationImpact = Field(..., description="Actual impact")
    status: str = Field(..., description="Implementation status")
    metrics_before: Dict[str, Any] = Field(..., description="Metrics before optimization")
    metrics_after: Dict[str, Any] = Field(..., description="Metrics after optimization")

class OptimizationHistoryResponse(BaseModel):
    """Optimization history response schema."""
    entries: List[OptimizationHistoryEntry] = Field(..., description="History entries")
    summary: Dict[str, Any] = Field(..., description="Historical summary")
    trends: Dict[str, Any] = Field(..., description="Optimization trends")

class ResourcePrediction(BaseModel):
    """Resource prediction schema."""
    resource_type: str = Field(..., description="Resource type")
    predicted_demand: List[Dict[str, Any]] = Field(..., description="Demand predictions")
    confidence_intervals: Dict[str, List[float]] = Field(..., description="Confidence intervals")
    seasonality: Optional[Dict[str, Any]] = Field(None, description="Seasonality patterns")
    trends: Dict[str, Any] = Field(..., description="Identified trends")

class ResourcePredictionResponse(BaseModel):
    """Resource prediction response schema."""
    predictions: List[ResourcePrediction] = Field(..., description="Resource predictions")
    confidence_intervals: Dict[str, List[float]] = Field(..., description="Overall confidence intervals")
    recommendations: List[Dict[str, Any]] = Field(..., description="Resource recommendations") 