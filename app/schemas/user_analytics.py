"""
User Analytics Schemas

This module defines Pydantic schemas for user analytics.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UserActivityMetrics(BaseModel):
    """Schema for user activity metrics."""
    user_id: int = Field(..., description="User ID")
    period_days: int = Field(..., description="Analysis period in days")
    total_sessions: int = Field(..., description="Total number of sessions")
    total_duration_hours: float = Field(..., description="Total session duration in hours")
    avg_session_duration_minutes: float = Field(..., description="Average session duration in minutes")
    daily_activity: Dict[str, int] = Field(..., description="Daily activity count")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")


class UserUsageAnalytics(BaseModel):
    """Schema for user usage analytics."""
    user_id: int = Field(..., description="User ID")
    period_days: int = Field(..., description="Analysis period in days")
    total_organizations: int = Field(..., description="Total organizations user belongs to")
    total_teams: int = Field(..., description="Total teams user belongs to")
    organization_roles: Dict[str, int] = Field(..., description="Role distribution in organizations")
    team_roles: Dict[str, int] = Field(..., description="Role distribution in teams")
    subscription_status: Optional[str] = Field(None, description="User subscription status")
    user_type: Optional[str] = Field(None, description="User type")
    billing_tier: Optional[str] = Field(None, description="Billing tier")


class UserPerformanceMetrics(BaseModel):
    """Schema for user performance metrics."""
    user_id: int = Field(..., description="User ID")
    period_days: int = Field(..., description="Analysis period in days")
    completion_rate: float = Field(..., description="Task completion rate")
    accuracy_score: float = Field(..., description="Accuracy score")
    efficiency_score: float = Field(..., description="Efficiency score")
    overall_score: float = Field(..., description="Overall performance score")
    profile_completeness: float = Field(..., description="Profile completeness percentage")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")


class UserEngagementData(BaseModel):
    """Schema for user engagement data."""
    user_id: int = Field(..., description="User ID")
    period_days: int = Field(..., description="Analysis period in days")
    total_days_active: int = Field(..., description="Total days user was active")
    engagement_rate: float = Field(..., description="Engagement rate (days active / total days)")
    session_frequency: float = Field(..., description="Average sessions per day")
    recent_activity: List[Dict[str, Any]] = Field(..., description="Recent activity data")
    is_active: bool = Field(..., description="Whether user is currently active")


class UserGrowthMetrics(BaseModel):
    """Schema for user growth metrics."""
    user_id: int = Field(..., description="User ID")
    period_days: int = Field(..., description="Analysis period in days")
    account_age_days: int = Field(..., description="Account age in days")
    skill_progression: float = Field(..., description="Skill progression score")
    feature_adoption: float = Field(..., description="Feature adoption rate")
    community_participation: float = Field(..., description="Community participation score")
    overall_growth: float = Field(..., description="Overall growth score")
    created_at: Optional[datetime] = Field(None, description="Account creation date")


class UserAnalyticsSummary(BaseModel):
    """Schema for user analytics summary."""
    user_id: int
    period_days: int
    overall_score: float
    activity_level: str  # high, medium, low
    engagement_level: str  # high, medium, low
    growth_potential: str  # high, medium, low
    key_metrics: Dict[str, Any]
    recommendations: List[str]


class UserAnalyticsComparison(BaseModel):
    """Schema for user analytics comparison."""
    user_ids: List[int] = Field(..., description="User IDs to compare")
    period_days: int = Field(..., description="Analysis period in days")
    comparison_data: Dict[str, Any] = Field(..., description="Comparison data")
    comparative_metrics: Optional[Dict[str, Any]] = Field(None, description="Comparative metrics")


class UserAnalyticsFilter(BaseModel):
    """Schema for user analytics filtering."""
    user_ids: Optional[List[int]] = Field(None, description="Filter by user IDs")
    date_from: Optional[datetime] = Field(None, description="Start date")
    date_to: Optional[datetime] = Field(None, description="End date")
    activity_level: Optional[str] = Field(None, description="Filter by activity level")
    engagement_level: Optional[str] = Field(None, description="Filter by engagement level")
    subscription_status: Optional[str] = Field(None, description="Filter by subscription status")
    user_type: Optional[str] = Field(None, description="Filter by user type")


class UserAnalyticsExport(BaseModel):
    """Schema for user analytics export."""
    user_id: int
    export_type: str  # activity, usage, performance, engagement, growth, comprehensive
    period_days: int
    data: Dict[str, Any]
    exported_at: datetime
    format: str = "json"  # json, csv, excel


class UserAnalyticsReport(BaseModel):
    """Schema for user analytics report."""
    report_id: str
    user_id: int
    report_type: str
    period_days: int
    generated_at: datetime
    data: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    charts: List[Dict[str, Any]]


class UserActivityLog(BaseModel):
    """Schema for user activity log entry."""
    user_id: int
    activity_type: str
    description: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class UserBehaviorPattern(BaseModel):
    """Schema for user behavior pattern."""
    user_id: int
    pattern_type: str  # login_time, feature_usage, session_duration, etc.
    pattern_data: Dict[str, Any]
    confidence_score: float
    detected_at: datetime
    is_active: bool


class UserRetentionMetrics(BaseModel):
    """Schema for user retention metrics."""
    user_id: int
    cohort_date: date
    retention_days: List[int]  # 1, 7, 30, 90 days
    retention_rates: List[float]
    churn_probability: float
    lifetime_value: Optional[float] = None
    predicted_churn_date: Optional[datetime] = None


class UserSegmentationData(BaseModel):
    """Schema for user segmentation data."""
    user_id: int
    segment: str  # power_user, casual_user, new_user, etc.
    segment_score: float
    segment_criteria: Dict[str, Any]
    assigned_at: datetime
    segment_characteristics: Dict[str, Any]


class UserPredictiveAnalytics(BaseModel):
    """Schema for user predictive analytics."""
    user_id: int
    churn_probability: float
    next_purchase_probability: float
    feature_adoption_prediction: Dict[str, float]
    engagement_prediction: float
    lifetime_value_prediction: float
    confidence_scores: Dict[str, float]
    prediction_date: datetime
    model_version: str 