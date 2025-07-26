"""
User Analytics Models - Phase 3

This module contains database models for user analytics, behavior tracking,
performance metrics, and intelligence data.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app.models.shared_base import SharedBase as Base


class UserActivity(Base):
    """Model for tracking user activity events."""
    
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    activity_type = Column(String(100), nullable=False, index=True)
    activity_data = Column(JSON, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    location_data = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "activity_data": self.activity_data,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "location_data": self.location_data
        }


class UserBehavior(Base):
    """Model for storing user behavior analysis."""
    
    __tablename__ = "user_behaviors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    behavior_type = Column(String(100), nullable=False, index=True)
    behavior_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    analysis_period = Column(String(20), default="30d")  # 7d, 30d, 90d
    
    # Relationships
    user = relationship("User", back_populates="behaviors")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "behavior_type": self.behavior_type,
            "behavior_data": self.behavior_data,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "analysis_period": self.analysis_period
        }


class UserPerformance(Base):
    """Model for storing user performance metrics."""
    
    __tablename__ = "user_performances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    accuracy = Column(Float, default=0.0)
    speed = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    efficiency = Column(Float, default=0.0)
    skill_levels = Column(JSON, nullable=True)
    performance_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    context = Column(String(100), nullable=True)  # e.g., "lesson", "assessment", "practice"
    
    # Relationships
    user = relationship("User", back_populates="performances")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "accuracy": self.accuracy,
            "speed": self.speed,
            "completion_rate": self.completion_rate,
            "efficiency": self.efficiency,
            "skill_levels": self.skill_levels,
            "performance_data": self.performance_data,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "context": self.context
        }


class UserEngagement(Base):
    """Model for storing user engagement metrics."""
    
    __tablename__ = "user_engagements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    engagement_score = Column(Float, default=0.0)
    session_count = Column(Integer, default=0)
    avg_session_duration = Column(Float, default=0.0)
    feature_usage = Column(JSON, nullable=True)
    retention_metrics = Column(JSON, nullable=True)
    churn_risk = Column(String(20), default="low")  # low, medium, high
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    period = Column(String(20), default="daily")  # daily, weekly, monthly
    
    # Relationships
    user = relationship("User", back_populates="engagements")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "engagement_score": self.engagement_score,
            "session_count": self.session_count,
            "avg_session_duration": self.avg_session_duration,
            "feature_usage": self.feature_usage,
            "retention_metrics": self.retention_metrics,
            "churn_risk": self.churn_risk,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "period": self.period
        }


class UserPrediction(Base):
    """Model for storing AI-generated user predictions."""
    
    __tablename__ = "user_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prediction_type = Column(String(100), nullable=False, index=True)  # behavior, performance, churn, etc.
    prediction_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=0.0)
    prediction_horizon = Column(String(20), default="30d")  # 7d, 30d, 90d
    model_version = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "prediction_type": self.prediction_type,
            "prediction_data": self.prediction_data,
            "confidence_score": self.confidence_score,
            "prediction_horizon": self.prediction_horizon,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_active": self.is_active
        }


class UserRecommendation(Base):
    """Model for storing AI-generated user recommendations."""
    
    __tablename__ = "user_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recommendation_type = Column(String(100), nullable=False, index=True)  # improvement, feature, content, etc.
    recommendation_data = Column(JSON, nullable=False)
    priority_score = Column(Float, default=0.0)
    category = Column(String(100), nullable=True)
    actionable_items = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recommendation_type": self.recommendation_type,
            "recommendation_data": self.recommendation_data,
            "priority_score": self.priority_score,
            "category": self.category,
            "actionable_items": self.actionable_items,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_implemented": self.is_implemented,
            "implementation_date": self.implementation_date.isoformat() if self.implementation_date else None
        }


class AnalyticsEvent(Base):
    """Model for tracking detailed analytics events."""
    
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON, nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(100), nullable=True)  # web, mobile, api, etc.
    version = Column(String(20), nullable=True)
    event_metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="analytics_events")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "version": self.version,
            "event_metadata": self.event_metadata
        }


class UserInsight(Base):
    """Model for storing user insights and intelligence."""
    
    __tablename__ = "user_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False, index=True)  # behavior, performance, trend, etc.
    insight_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=0.0)
    key_findings = Column(JSON, nullable=True)
    improvement_areas = Column(JSON, nullable=True)
    strengths = Column(JSON, nullable=True)
    opportunities = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_actionable = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="insights")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "insight_type": self.insight_type,
            "insight_data": self.insight_data,
            "confidence_score": self.confidence_score,
            "key_findings": self.key_findings,
            "improvement_areas": self.improvement_areas,
            "strengths": self.strengths,
            "opportunities": self.opportunities,
            "risk_factors": self.risk_factors,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_actionable": self.is_actionable
        }


class UserTrend(Base):
    """Model for storing user trends and patterns."""
    
    __tablename__ = "user_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    trend_type = Column(String(100), nullable=False, index=True)  # activity, performance, engagement, etc.
    trend_data = Column(JSON, nullable=False)
    trend_direction = Column(String(20), nullable=False)  # increasing, decreasing, stable
    trend_strength = Column(Float, default=0.0)
    seasonal_patterns = Column(JSON, nullable=True)
    time_range = Column(String(20), default="30d")  # 7d, 30d, 90d
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="trends")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "trend_type": self.trend_type,
            "trend_data": self.trend_data,
            "trend_direction": self.trend_direction,
            "trend_strength": self.trend_strength,
            "seasonal_patterns": self.seasonal_patterns,
            "time_range": self.time_range,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class UserComparison(Base):
    """Model for storing user comparison data."""
    
    __tablename__ = "user_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    comparison_type = Column(String(100), nullable=False, index=True)  # peer, benchmark, historical, etc.
    comparison_data = Column(JSON, nullable=False)
    comparison_users = Column(JSON, nullable=True)  # List of user IDs being compared
    percentile_rank = Column(Float, default=0.0)
    benchmarking_data = Column(JSON, nullable=True)
    insights = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="comparisons")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "comparison_type": self.comparison_type,
            "comparison_data": self.comparison_data,
            "comparison_users": self.comparison_users,
            "percentile_rank": self.percentile_rank,
            "benchmarking_data": self.benchmarking_data,
            "insights": self.insights,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        } 