"""
Analytics Schemas

This module provides Pydantic models for analytics-related data validation
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MetricBase(BaseModel):
    """Base metrics schema."""
    total: int = Field(..., description="Total count")
    active: int = Field(..., description="Active count")
    by_type: Dict[str, int] = Field(..., description="Counts by type")

class MemberMetrics(MetricBase):
    """Member metrics schema."""
    growth_rate: float = Field(..., description="Member growth rate")
    engagement_rate: float = Field(..., description="Member engagement rate")

class CollaborationMetrics(MetricBase):
    """Collaboration metrics schema."""
    success_rate: float = Field(..., description="Collaboration success rate")
    avg_duration: float = Field(..., description="Average collaboration duration in days")

class ResourceMetrics(MetricBase):
    """Resource metrics schema."""
    utilization_rate: float = Field(..., description="Resource utilization rate")
    efficiency_score: float = Field(..., description="Resource efficiency score")

class OrganizationSummary(BaseModel):
    """Organization summary schema."""
    id: int = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    type: str = Field(..., description="Organization type")
    subscription_tier: str = Field(..., description="Subscription tier")
    member_count: int = Field(..., description="Total member count")
    department_count: int = Field(..., description="Total department count")
    resource_count: int = Field(..., description="Total resource count")

class OrganizationMetricsResponse(BaseModel):
    """Organization metrics response schema."""
    organization: OrganizationSummary = Field(..., description="Organization summary")
    members: MemberMetrics = Field(..., description="Member metrics")
    collaborations: CollaborationMetrics = Field(..., description="Collaboration metrics")
    resources: ResourceMetrics = Field(..., description="Resource metrics")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
    engagement: Dict[str, Any] = Field(..., description="Engagement metrics")
    trends: Dict[str, Any] = Field(..., description="Trend analysis")

class CollaborationPattern(BaseModel):
    """Collaboration pattern schema."""
    pattern_type: str = Field(..., description="Pattern type")
    frequency: int = Field(..., description="Pattern frequency")
    impact_score: float = Field(..., description="Pattern impact score")
    description: str = Field(..., description="Pattern description")

class CollaborationEffectiveness(BaseModel):
    """Collaboration effectiveness schema."""
    overall_score: float = Field(..., description="Overall effectiveness score")
    key_factors: List[Dict[str, Any]] = Field(..., description="Key contributing factors")
    areas_for_improvement: List[str] = Field(..., description="Areas needing improvement")

class CollaborationAnalyticsResponse(BaseModel):
    """Collaboration analytics response schema."""
    overview: Dict[str, Any] = Field(..., description="Collaboration overview")
    patterns: List[CollaborationPattern] = Field(..., description="Collaboration patterns")
    effectiveness: CollaborationEffectiveness = Field(..., description="Collaboration effectiveness")
    resource_sharing: Dict[str, Any] = Field(..., description="Resource sharing analysis")
    communication: Dict[str, Any] = Field(..., description="Communication patterns")
    recommendations: List[Dict[str, Any]] = Field(..., description="Recommendations")

class ResourceUsage(BaseModel):
    """Resource usage schema."""
    resource_type: str = Field(..., description="Resource type")
    usage_metrics: Dict[str, Any] = Field(..., description="Usage metrics")
    trends: Dict[str, Any] = Field(..., description="Usage trends")
    bottlenecks: List[str] = Field(..., description="Identified bottlenecks")

class ResourceEfficiency(BaseModel):
    """Resource efficiency schema."""
    overall_score: float = Field(..., description="Overall efficiency score")
    metrics_by_type: Dict[str, float] = Field(..., description="Efficiency metrics by type")
    improvement_areas: List[str] = Field(..., description="Areas for improvement")

class ResourceAnalyticsResponse(BaseModel):
    """Resource analytics response schema."""
    usage: List[ResourceUsage] = Field(..., description="Resource usage analysis")
    allocation: Dict[str, Any] = Field(..., description="Resource allocation analysis")
    efficiency: ResourceEfficiency = Field(..., description="Resource efficiency analysis")
    optimization: List[Dict[str, Any]] = Field(..., description="Optimization suggestions")
    predictions: Dict[str, Any] = Field(..., description="Resource needs predictions")

class PerformanceMetrics(BaseModel):
    """Performance metrics schema."""
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current metric value")
    trend: str = Field(..., description="Metric trend")
    benchmark: float = Field(..., description="Benchmark value")
    status: str = Field(..., description="Performance status")

class PerformanceTrend(BaseModel):
    """Performance trend schema."""
    metric: str = Field(..., description="Metric name")
    data_points: List[Dict[str, Any]] = Field(..., description="Historical data points")
    trend_line: Dict[str, Any] = Field(..., description="Trend line data")
    seasonality: Optional[Dict[str, Any]] = Field(None, description="Seasonality analysis")

class PerformanceReportResponse(BaseModel):
    """Performance report response schema."""
    summary: Dict[str, Any] = Field(..., description="Performance summary")
    metrics: List[PerformanceMetrics] = Field(..., description="Detailed metrics")
    analysis: List[PerformanceTrend] = Field(..., description="Trend analysis")
    benchmarks: Dict[str, Any] = Field(..., description="Benchmark comparisons")
    recommendations: List[Dict[str, Any]] = Field(..., description="Performance recommendations")
    predictions: Optional[Dict[str, Any]] = Field(None, description="Performance predictions") 