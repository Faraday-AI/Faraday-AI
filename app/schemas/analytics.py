"""
Analytics Schemas - Phase 3

This module contains Pydantic schemas for user analytics, behavior tracking,
performance metrics, and intelligence data.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class TimeRange(str, Enum):
    """Time range options for analytics."""
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"
    ONE_YEAR = "1y"


class TrendDirection(str, Enum):
    """Trend direction options."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    INSUFFICIENT_DATA = "insufficient_data"


class RiskLevel(str, Enum):
    """Risk level options."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PerformanceRating(str, Enum):
    """Performance rating options."""
    EXCELLENT = "excellent"
    ABOVE_AVERAGE = "above_average"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"


# Base Models
class AnalyticsEventBase(BaseModel):
    """Base model for analytics events."""
    event_type: str = Field(..., description="Type of analytics event")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event data")
    session_id: Optional[str] = Field(None, description="Session identifier")
    source: Optional[str] = Field(None, description="Event source")
    version: Optional[str] = Field(None, description="Application version")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AnalyticsEventCreate(AnalyticsEventBase):
    """Schema for creating analytics events."""
    user_id: int = Field(..., description="User ID")


class AnalyticsEventResponse(AnalyticsEventBase):
    """Schema for analytics event responses."""
    id: int
    user_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# User Analytics Response Models
class UserAnalyticsResponse(BaseModel):
    """Comprehensive user analytics response."""
    user_id: int
    time_range: str
    total_activities: int
    unique_sessions: int
    activity_types: Dict[str, int]
    daily_activity: Dict[str, int]
    peak_activity_hour: int
    engagement_score: float
    performance_metrics: Dict[str, Any]
    behavior_analysis: Dict[str, Any]
    last_activity: Optional[datetime]
    profile_completeness: float
    
    class Config:
        from_attributes = True


class UserBehaviorAnalysis(BaseModel):
    """User behavior analysis response."""
    user_id: int
    time_range: str
    patterns: Dict[str, Any]
    insights: List[str]
    behavior_score: float
    consistency_score: float
    
    class Config:
        from_attributes = True


class UserPerformanceMetrics(BaseModel):
    """User performance metrics response."""
    user_id: int
    time_range: str
    metrics: Dict[str, Any]
    trends: Dict[str, Any]
    benchmarks: Dict[str, Any]
    overall_score: float
    percentile_rank: float
    
    class Config:
        from_attributes = True


class UserEngagementMetrics(BaseModel):
    """User engagement metrics response."""
    user_id: int
    time_range: str
    daily_engagement: Dict[str, Any]
    feature_engagement: Dict[str, Any]
    session_engagement: Dict[str, Any]
    engagement_score: float
    retention_metrics: Dict[str, Any]
    churn_risk: Dict[str, Any]
    engagement_trend: str
    
    class Config:
        from_attributes = True


class UserPredictionResponse(BaseModel):
    """User prediction response."""
    user_id: int
    predictions: Dict[str, Any]
    confidence_score: float
    prediction_horizon: str
    last_updated: datetime
    
    class Config:
        from_attributes = True


class UserRecommendationResponse(BaseModel):
    """User recommendation response."""
    user_id: int
    recommendations: Dict[str, Any]
    priority_score: float
    categories: List[str]
    actionable_items: List[str]
    last_updated: datetime
    
    class Config:
        from_attributes = True


class UserInsightsResponse(BaseModel):
    """User insights response."""
    user_id: int
    insights: Dict[str, Any]
    key_findings: List[str]
    improvement_areas: List[str]
    strengths: List[str]
    opportunities: List[str]
    risk_factors: List[str]
    success_indicators: List[str]
    generated_at: datetime
    
    class Config:
        from_attributes = True


class UserTrendsResponse(BaseModel):
    """User trends response."""
    user_id: int
    time_range: str
    trends: Dict[str, Any]
    trend_direction: str
    trend_strength: float
    seasonal_patterns: Dict[str, Any]
    generated_at: datetime
    
    class Config:
        from_attributes = True


class UserComparisonResponse(BaseModel):
    """User comparison response."""
    user_id: int
    comparison_users: List[int]
    comparison_data: List[Dict[str, Any]]
    insights: Dict[str, Any]
    relative_performance: Dict[str, Any]
    benchmarking_data: Dict[str, Any]
    generated_at: datetime
    
    class Config:
        from_attributes = True


# Detailed Analysis Models
class SessionAnalysis(BaseModel):
    """Session analysis model."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    activity_count: int
    features_used: List[str]
    engagement_score: float
    
    class Config:
        from_attributes = True


class FeatureUsageAnalysis(BaseModel):
    """Feature usage analysis model."""
    feature_name: str
    usage_count: int
    usage_frequency: float
    user_satisfaction: Optional[float]
    completion_rate: Optional[float]
    time_spent: Optional[float]
    
    class Config:
        from_attributes = True


class PerformanceTrend(BaseModel):
    """Performance trend model."""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend_direction: TrendDirection
    trend_strength: float
    confidence_interval: Optional[Dict[str, float]]
    
    class Config:
        from_attributes = True


class BehavioralPattern(BaseModel):
    """Behavioral pattern model."""
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence_score: float
    frequency: float
    consistency: float
    last_observed: datetime
    
    class Config:
        from_attributes = True


class EngagementPattern(BaseModel):
    """Engagement pattern model."""
    pattern_type: str
    daily_pattern: Dict[str, int]
    weekly_pattern: Dict[str, int]
    peak_hours: List[int]
    engagement_score: float
    retention_impact: float
    
    class Config:
        from_attributes = True


# Prediction Models
class BehaviorPrediction(BaseModel):
    """Behavior prediction model."""
    prediction_type: str
    predicted_value: Any
    confidence_score: float
    prediction_horizon: str
    factors: List[str]
    impact_score: float
    
    class Config:
        from_attributes = True


class PerformancePrediction(BaseModel):
    """Performance prediction model."""
    metric_name: str
    predicted_value: float
    confidence_score: float
    prediction_horizon: str
    improvement_potential: float
    recommended_actions: List[str]
    
    class Config:
        from_attributes = True


class ChurnPrediction(BaseModel):
    """Churn prediction model."""
    churn_probability: float
    risk_level: RiskLevel
    risk_factors: List[str]
    prediction_horizon: str
    confidence_score: float
    mitigation_strategies: List[str]
    
    class Config:
        from_attributes = True


# Recommendation Models
class ImprovementRecommendation(BaseModel):
    """Improvement recommendation model."""
    category: str
    title: str
    description: str
    priority_score: float
    expected_impact: float
    implementation_effort: str
    actionable_items: List[str]
    success_metrics: List[str]
    
    class Config:
        from_attributes = True


class FeatureRecommendation(BaseModel):
    """Feature recommendation model."""
    feature_name: str
    recommendation_reason: str
    expected_benefit: str
    priority_score: float
    user_segment: str
    implementation_priority: str
    
    class Config:
        from_attributes = True


class ContentRecommendation(BaseModel):
    """Content recommendation model."""
    content_type: str
    content_id: str
    title: str
    description: str
    relevance_score: float
    difficulty_level: str
    estimated_duration: int
    learning_objectives: List[str]
    
    class Config:
        from_attributes = True


# Insight Models
class UserInsight(BaseModel):
    """User insight model."""
    insight_type: str
    title: str
    description: str
    confidence_score: float
    impact_score: float
    actionable: bool
    category: str
    supporting_data: Dict[str, Any]
    
    class Config:
        from_attributes = True


class TrendInsight(BaseModel):
    """Trend insight model."""
    trend_type: str
    direction: TrendDirection
    strength: float
    duration: str
    significance: float
    implications: List[str]
    recommendations: List[str]
    
    class Config:
        from_attributes = True


class ComparativeInsight(BaseModel):
    """Comparative insight model."""
    comparison_type: str
    user_percentile: float
    relative_performance: str
    strengths: List[str]
    areas_for_improvement: List[str]
    benchmarking_data: Dict[str, Any]
    
    class Config:
        from_attributes = True


# Request Models
class AnalyticsRequest(BaseModel):
    """Base analytics request model."""
    time_range: TimeRange = Field(default=TimeRange.THIRTY_DAYS, description="Time range for analysis")
    include_predictions: bool = Field(default=True, description="Include AI predictions")
    include_recommendations: bool = Field(default=True, description="Include AI recommendations")
    include_insights: bool = Field(default=True, description="Include AI insights")


class UserAnalyticsRequest(AnalyticsRequest):
    """User analytics request model."""
    user_id: int = Field(..., description="User ID for analysis")


class BehaviorAnalysisRequest(AnalyticsRequest):
    """Behavior analysis request model."""
    user_id: int = Field(..., description="User ID for behavior analysis")
    include_patterns: bool = Field(default=True, description="Include behavior patterns")
    include_insights: bool = Field(default=True, description="Include behavioral insights")


class PerformanceAnalysisRequest(AnalyticsRequest):
    """Performance analysis request model."""
    user_id: int = Field(..., description="User ID for performance analysis")
    include_benchmarks: bool = Field(default=True, description="Include performance benchmarks")
    include_trends: bool = Field(default=True, description="Include performance trends")


class EngagementAnalysisRequest(AnalyticsRequest):
    """Engagement analysis request model."""
    user_id: int = Field(..., description="User ID for engagement analysis")
    include_retention: bool = Field(default=True, description="Include retention metrics")
    include_churn_risk: bool = Field(default=True, description="Include churn risk assessment")


class PredictionRequest(BaseModel):
    """Prediction request model."""
    user_id: int = Field(..., description="User ID for predictions")
    prediction_types: List[str] = Field(default=["behavior", "performance", "churn"], 
                                       description="Types of predictions to generate")
    prediction_horizon: str = Field(default="30d", description="Prediction horizon")


class RecommendationRequest(BaseModel):
    """Recommendation request model."""
    user_id: int = Field(..., description="User ID for recommendations")
    recommendation_types: List[str] = Field(default=["improvement", "feature", "content"], 
                                           description="Types of recommendations to generate")
    priority_threshold: float = Field(default=0.5, description="Minimum priority score")


class ComparisonRequest(BaseModel):
    """Comparison request model."""
    user_id: int = Field(..., description="Primary user ID")
    comparison_users: List[int] = Field(..., description="User IDs to compare against")
    comparison_types: List[str] = Field(default=["performance", "engagement", "behavior"], 
                                       description="Types of comparisons to generate")


class TrendAnalysisRequest(BaseModel):
    """Trend analysis request model."""
    user_id: int = Field(..., description="User ID for trend analysis")
    time_range: TimeRange = Field(default=TimeRange.NINETY_DAYS, description="Time range for trend analysis")
    trend_types: List[str] = Field(default=["activity", "performance", "engagement"], 
                                  description="Types of trends to analyze")
    include_seasonal: bool = Field(default=True, description="Include seasonal pattern analysis")


# Response Models for API Endpoints
class AnalyticsSummaryResponse(BaseModel):
    """Analytics summary response."""
    user_id: int
    total_analytics: int
    last_updated: datetime
    key_metrics: Dict[str, Any]
    recent_insights: List[str]
    upcoming_predictions: List[str]
    
    class Config:
        from_attributes = True


class AnalyticsExportResponse(BaseModel):
    """Analytics export response."""
    user_id: int
    export_type: str
    data_format: str
    download_url: str
    file_size: int
    expires_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsHealthResponse(BaseModel):
    """Analytics system health response."""
    system_status: str
    data_freshness: datetime
    model_versions: Dict[str, str]
    prediction_accuracy: float
    recommendation_effectiveness: float
    system_performance: Dict[str, Any]
    
    class Config:
        from_attributes = True


# Validation Models
class AnalyticsEventValidation(BaseModel):
    """Analytics event validation model."""
    event_type: str = Field(..., min_length=1, max_length=100)
    event_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = Field(None, max_length=255)
    
    @validator('event_type')
    def validate_event_type(cls, v):
        allowed_types = [
            'page_view', 'button_click', 'form_submit', 'api_call', 
            'login', 'logout', 'feature_usage', 'error', 'performance'
        ]
        if v not in allowed_types:
            raise ValueError(f'Event type must be one of: {allowed_types}')
        return v


class TimeRangeValidation(BaseModel):
    """Time range validation model."""
    time_range: TimeRange
    
    @validator('time_range')
    def validate_time_range(cls, v):
        return v


# Utility Models
class AnalyticsFilter(BaseModel):
    """Analytics filter model."""
    user_ids: Optional[List[int]] = None
    event_types: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    session_ids: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class AnalyticsAggregation(BaseModel):
    """Analytics aggregation model."""
    group_by: str
    aggregation_type: str  # count, sum, average, min, max
    metric: str
    time_interval: Optional[str] = None  # hourly, daily, weekly, monthly
    
    class Config:
        from_attributes = True


class AnalyticsSort(BaseModel):
    """Analytics sort model."""
    field: str
    direction: str = "desc"  # asc, desc
    
    class Config:
        from_attributes = True


class AnalyticsPagination(BaseModel):
    """Analytics pagination model."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)
    total_count: Optional[int] = None
    
    class Config:
        from_attributes = True 