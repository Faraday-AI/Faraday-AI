"""
Optimization Monitoring Schemas

This module provides Pydantic schemas for the optimization monitoring service.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Anomaly(BaseModel):
    """Resource usage anomaly."""
    timestamp: datetime = Field(..., description="Anomaly timestamp")
    resource_type: str = Field(..., description="Resource type")
    usage_amount: float = Field(..., description="Usage amount")
    severity: str = Field(..., description="Anomaly severity")

class Recommendation(BaseModel):
    """Optimization recommendation."""
    type: str = Field(..., description="Recommendation type")
    priority: str = Field(..., description="Recommendation priority")
    message: str = Field(..., description="Recommendation message")

class UsagePatterns(BaseModel):
    """Resource usage patterns."""
    peak_hours: List[int] = Field(..., description="Peak usage hours")
    resource_distribution: Dict[str, int] = Field(..., description="Resource type distribution")
    usage_trend: Dict[str, float] = Field(..., description="Usage trend")

class SharingPatterns(BaseModel):
    """Resource sharing patterns."""
    frequent_partners: Dict[str, int] = Field(..., description="Frequent sharing partners")
    resource_preferences: Dict[str, int] = Field(..., description="Resource type preferences")
    sharing_trend: Dict[str, float] = Field(..., description="Sharing trend")

class Trend(BaseModel):
    """Resource trend."""
    direction: str = Field(..., description="Trend direction")
    rate: float = Field(..., description="Trend rate")

class OverallTrend(BaseModel):
    """Overall optimization trend."""
    score: float = Field(..., description="Trend score")
    direction: str = Field(..., description="Trend direction")
    confidence: float = Field(..., description="Trend confidence")

class Opportunity(BaseModel):
    """Optimization opportunity."""
    type: str = Field(..., description="Opportunity type")
    priority: str = Field(..., description="Opportunity priority")
    message: str = Field(..., description="Opportunity message")

class Risk(BaseModel):
    """Optimization risk."""
    type: str = Field(..., description="Risk type")
    severity: str = Field(..., description="Risk severity")
    message: str = Field(..., description="Risk message")

class OptimizationMetricsResponse(BaseModel):
    """Response model for optimization metrics."""
    utilization_rate: float = Field(..., description="Resource utilization rate")
    sharing_efficiency: float = Field(..., description="Resource sharing efficiency")
    optimization_score: float = Field(..., description="Overall optimization score")
    anomalies: Optional[List[Anomaly]] = Field(None, description="Detected anomalies")
    recommendations: Optional[List[Recommendation]] = Field(None, description="Optimization recommendations")
    timestamp: datetime = Field(..., description="Metrics timestamp")

class OptimizationInsightsResponse(BaseModel):
    """Response model for optimization insights."""
    patterns: Optional[Dict[str, Any]] = Field(None, description="Usage and sharing patterns")
    trends: Optional[Dict[str, Any]] = Field(None, description="Usage and sharing trends")
    opportunities: Optional[List[Opportunity]] = Field(None, description="Optimization opportunities")
    risks: Optional[List[Risk]] = Field(None, description="Optimization risks")
    timestamp: datetime = Field(..., description="Insights timestamp") 