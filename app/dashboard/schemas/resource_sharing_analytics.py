"""Resource sharing analytics schemas."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ResourceUsageMetrics(BaseModel):
    """Resource usage metrics over time."""
    total_usage: float = Field(..., description="Total resource usage")
    average_usage: float = Field(..., description="Average resource usage")
    peak_usage: float = Field(..., description="Peak resource usage")
    usage_by_type: Dict[str, float] = Field(..., description="Usage breakdown by resource type")
    timestamp: datetime = Field(..., description="Metrics timestamp")

class ResourceSharingPatterns(BaseModel):
    """Resource sharing patterns analysis."""
    frequent_pairs: List[Dict[str, str]] = Field(..., description="Frequently sharing organization pairs")
    sharing_frequency: Dict[str, float] = Field(..., description="Sharing frequency by organization")
    resource_popularity: Dict[str, float] = Field(..., description="Resource popularity metrics")
    timestamp: datetime = Field(..., description="Analysis timestamp")

class ResourceEfficiencyMetrics(BaseModel):
    """Resource efficiency metrics."""
    utilization_rate: float = Field(..., description="Resource utilization rate")
    sharing_efficiency: float = Field(..., description="Resource sharing efficiency score")
    cost_savings: float = Field(..., description="Estimated cost savings from sharing")
    optimization_score: float = Field(..., description="Resource optimization score")
    timestamp: datetime = Field(..., description="Metrics timestamp")

class ResourceSharingTrends(BaseModel):
    """Resource sharing trend analysis."""
    usage_trend: List[Dict[str, float]] = Field(..., description="Usage trend over time")
    sharing_trend: List[Dict[str, float]] = Field(..., description="Sharing trend over time")
    efficiency_trend: List[Dict[str, float]] = Field(..., description="Efficiency trend over time")
    timestamp: datetime = Field(..., description="Analysis timestamp")

class ResourceSharingAnalytics(BaseModel):
    """Resource sharing analytics data."""
    usage_metrics: Dict[str, Dict[str, float]]
    timestamp: datetime
    sharing_patterns: Optional[Dict[str, Dict[str, float]]] = None
    efficiency_metrics: Optional[Dict[str, Dict[str, float]]] = None
    trends: Optional[Dict[str, List[float]]] = None 