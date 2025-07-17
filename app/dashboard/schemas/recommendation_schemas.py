"""
Recommendation Schemas

This module provides Pydantic models for recommendation-related data validation
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class GPTRecommendation(BaseModel):
    """Schema for GPT recommendation."""
    gpt_id: str = Field(..., description="GPT ID")
    name: str = Field(..., description="GPT name")
    description: str = Field(..., description="GPT description")
    confidence_score: float = Field(..., description="Recommendation confidence score")
    relevance_score: float = Field(..., description="Recommendation relevance score")
    match_score: float = Field(..., description="Overall match score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        from_attributes = True

class RecommendationScore(BaseModel):
    """Schema for recommendation scores."""
    overall_score: float = Field(..., description="Overall recommendation score")
    confidence: float = Field(..., description="Score confidence")
    breakdown: Optional[Dict[str, float]] = Field(None, description="Score breakdown by category")
    trends: Optional[Dict[str, List[float]]] = Field(None, description="Score trends over time")
    benchmarks: Optional[Dict[str, float]] = Field(None, description="Score benchmarks")
    correlations: Optional[Dict[str, float]] = Field(None, description="Score correlations")
    impact: Optional[Dict[str, Any]] = Field(None, description="Score impact analysis")

    class Config:
        from_attributes = True

class RecommendationContext(BaseModel):
    """Schema for recommendation context."""
    context_id: str = Field(..., description="Context ID")
    user_id: str = Field(..., description="User ID")
    history: Optional[List[Dict[str, Any]]] = Field(None, description="Context history")
    patterns: Optional[Dict[str, Any]] = Field(None, description="Usage patterns")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    insights: Optional[Dict[str, Any]] = Field(None, description="Context insights")
    optimization: Optional[Dict[str, Any]] = Field(None, description="Context optimization")

    class Config:
        from_attributes = True

class RecommendationMetrics(BaseModel):
    """Schema for recommendation metrics."""
    accuracy: Optional[Dict[str, float]] = Field(None, description="Accuracy metrics")
    relevance: Optional[Dict[str, float]] = Field(None, description="Relevance metrics")
    engagement: Optional[Dict[str, float]] = Field(None, description="Engagement metrics")
    efficiency: Optional[Dict[str, float]] = Field(None, description="Efficiency metrics")
    quality: Optional[Dict[str, float]] = Field(None, description="Quality metrics")
    impact: Optional[Dict[str, Any]] = Field(None, description="Impact metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")

    class Config:
        from_attributes = True

class RecommendationAnalytics(BaseModel):
    """Schema for recommendation analytics."""
    trends: Optional[Dict[str, List[float]]] = Field(None, description="Recommendation trends")
    patterns: Optional[Dict[str, Any]] = Field(None, description="Usage patterns")
    forecasts: Optional[Dict[str, Any]] = Field(None, description="Usage forecasts")
    correlations: Optional[Dict[str, float]] = Field(None, description="Metric correlations")
    anomalies: Optional[List[Dict[str, Any]]] = Field(None, description="Detected anomalies")
    insights: Optional[Dict[str, Any]] = Field(None, description="Analytics insights")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analytics timestamp")

    class Config:
        from_attributes = True

class RecommendationPerformance(BaseModel):
    """Schema for recommendation performance."""
    benchmarks: Optional[Dict[str, float]] = Field(None, description="Performance benchmarks")
    optimization: Optional[Dict[str, Any]] = Field(None, description="Optimization opportunities")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Performance recommendations")
    trends: Optional[Dict[str, List[float]]] = Field(None, description="Performance trends")
    impact: Optional[Dict[str, Any]] = Field(None, description="Performance impact")
    insights: Optional[Dict[str, Any]] = Field(None, description="Performance insights")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Performance timestamp")

    class Config:
        from_attributes = True

class RecommendationInsights(BaseModel):
    """Schema for recommendation insights."""
    trends: Optional[Dict[str, List[float]]] = Field(None, description="Insight trends")
    patterns: Optional[Dict[str, Any]] = Field(None, description="Usage patterns")
    opportunities: Optional[List[Dict[str, Any]]] = Field(None, description="Optimization opportunities")
    impact: Optional[Dict[str, Any]] = Field(None, description="Impact analysis")
    forecasts: Optional[Dict[str, Any]] = Field(None, description="Usage forecasts")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Insights timestamp")

    class Config:
        from_attributes = True

class RecommendationOptimization(BaseModel):
    """Schema for recommendation optimization."""
    opportunities: Optional[List[Dict[str, Any]]] = Field(None, description="Optimization opportunities")
    impact: Optional[Dict[str, Any]] = Field(None, description="Impact analysis")
    recommendations: Optional[List[Dict[str, Any]]] = Field(None, description="Optimization recommendations")
    metrics: Optional[Dict[str, float]] = Field(None, description="Optimization metrics")
    forecasts: Optional[Dict[str, Any]] = Field(None, description="Optimization forecasts")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Optimization timestamp")

    class Config:
        from_attributes = True 