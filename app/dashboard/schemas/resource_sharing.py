from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ResourceSharingWidgetBase(BaseModel):
    """Base schema for resource sharing widgets."""
    widget_type: str = Field(..., description="Type of resource sharing widget")
    configuration: Dict = Field(..., description="Widget configuration")
    position: Optional[Dict] = Field(None, description="Widget position on dashboard")
    size: Optional[Dict] = Field(None, description="Widget size on dashboard")

class ResourceSharingWidgetCreate(ResourceSharingWidgetBase):
    """Schema for creating a resource sharing widget."""
    pass

class ResourceSharingWidgetUpdate(BaseModel):
    """Schema for updating a resource sharing widget."""
    configuration: Optional[Dict] = Field(None, description="Updated widget configuration")
    position: Optional[Dict] = Field(None, description="Updated widget position")
    size: Optional[Dict] = Field(None, description="Updated widget size")

class ResourceSharingWidgetResponse(ResourceSharingWidgetBase):
    """Schema for resource sharing widget response."""
    id: str = Field(..., description="Widget ID")
    created_at: datetime = Field(..., description="Widget creation timestamp")
    updated_at: datetime = Field(..., description="Widget last update timestamp")

    class Config:
        from_attributes = True

class ResourceMetric(BaseModel):
    """Schema for a resource metric."""
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Metric unit")
    timestamp: datetime = Field(..., description="Metric timestamp")

class ResourceUsageResponse(BaseModel):
    """Schema for resource usage response."""
    metrics: Dict[str, ResourceMetric] = Field(..., description="Resource usage metrics")
    timestamp: datetime = Field(..., description="Response timestamp")

class OptimizationRecommendation(BaseModel):
    """Schema for optimization recommendation."""
    type: str = Field(..., description="Recommendation type")
    action: str = Field(..., description="Recommended action")
    resource: str = Field(..., description="Target resource")
    priority: Optional[str] = Field(None, description="Recommendation priority")
    impact: Optional[float] = Field(None, description="Expected impact")

class ResourceOptimizationResponse(BaseModel):
    """Schema for resource optimization response."""
    optimization: Dict[str, List[OptimizationRecommendation]] = Field(
        ..., 
        description="Optimization recommendations"
    )
    timestamp: datetime = Field(..., description="Response timestamp")

class ResourcePrediction(BaseModel):
    """Schema for resource prediction."""
    timestamp: datetime = Field(..., description="Prediction timestamp")
    value: float = Field(..., description="Predicted value")
    confidence: Optional[float] = Field(None, description="Prediction confidence")

class ResourcePredictionResponse(BaseModel):
    """Schema for resource prediction response."""
    predictions: Dict[str, List[ResourcePrediction]] = Field(
        ..., 
        description="Resource predictions"
    )
    timestamp: datetime = Field(..., description="Response timestamp")

class SharingPattern(BaseModel):
    """Schema for sharing pattern."""
    org_pair: List[str] = Field(..., description="Organization pair")
    frequency: str = Field(..., description="Sharing frequency")
    resources: List[str] = Field(..., description="Shared resources")
    trend: Optional[str] = Field(None, description="Pattern trend")
    efficiency: Optional[float] = Field(None, description="Sharing efficiency")

class CrossOrgPatternsResponse(BaseModel):
    """Schema for cross-organization patterns response."""
    patterns: Dict[str, List[SharingPattern]] = Field(
        ..., 
        description="Sharing patterns"
    )
    timestamp: datetime = Field(..., description="Response timestamp")

class SecurityVulnerability(BaseModel):
    """Schema for security vulnerability."""
    severity: str = Field(..., description="Vulnerability severity")
    description: str = Field(..., description="Vulnerability description")
    resource: str = Field(..., description="Affected resource")
    recommendation: str = Field(..., description="Security recommendation")

class SecurityMetricsResponse(BaseModel):
    """Schema for security metrics response."""
    security: Dict[str, Dict] = Field(..., description="Security metrics and recommendations")
    timestamp: datetime = Field(..., description="Response timestamp") 