"""
Engagement Models

This module contains models for tracking student engagement in activities.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class EngagementModel(Base):
    """Model for tracking student engagement in activities."""
    
    __tablename__ = "engagement"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), nullable=False, index=True)
    activity_id = Column(String(255), nullable=False, index=True)
    engagement_score = Column(Float, nullable=False, default=0.0)
    engagement_level = Column(String(50), nullable=False, default="low")
    participation_level = Column(Float, nullable=True)
    focus_duration = Column(Integer, nullable=True)  # in minutes
    interaction_count = Column(Integer, nullable=True)
    feedback_quality = Column(Float, nullable=True)
    engagement_metrics = Column(JSON, nullable=True)
    improvement_areas = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class EngagementPattern(Base):
    """Model for storing engagement pattern analysis."""
    
    __tablename__ = "engagement_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), nullable=False, index=True)
    activity_id = Column(String(255), nullable=False, index=True)
    pattern_type = Column(String(100), nullable=False)  # e.g., "daily", "weekly", "trend"
    pattern_data = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=True)
    analysis_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EngagementReport(Base):
    """Model for storing engagement reports."""
    
    __tablename__ = "engagement_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(255), unique=True, nullable=False, index=True)
    student_id = Column(String(255), nullable=False, index=True)
    activity_id = Column(String(255), nullable=False, index=True)
    report_type = Column(String(100), nullable=False)  # e.g., "summary", "detailed", "trend"
    report_data = Column(JSON, nullable=False)
    download_url = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EngagementPrediction(Base):
    """Model for storing engagement predictions."""
    
    __tablename__ = "engagement_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(255), nullable=False, index=True)
    activity_id = Column(String(255), nullable=False, index=True)
    prediction_type = Column(String(100), nullable=False)  # e.g., "trend", "next_session", "long_term"
    predicted_score = Column(Float, nullable=False)
    confidence_interval = Column(JSON, nullable=True)
    prediction_factors = Column(JSON, nullable=True)
    prediction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False) 