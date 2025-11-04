"""
Student Health Metric Models

This module defines student health metric models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

class HealthMetric(BaseModelMixin, TimestampMixin):
    """Model for health metrics."""
    __tablename__ = 'student_health_metrics'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # e.g., BMI, Heart Rate, Blood Pressure
    value = Column(Integer, nullable=False)
    unit = Column(String(20), nullable=False)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(String)

    # Relationships will be set up by setup_health_metric_relationships() after model initialization
    # This avoids circular import issues during SQLAlchemy mapper configuration
    pass  # Relationship added via setup_health_metric_relationships()

class HealthMetricHistory(BaseModelMixin, TimestampMixin):
    """Model for tracking student health metric history."""
    __tablename__ = 'student_health_metric_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey('fitness_health_metrics.id'), nullable=False)
    value = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(String)

    # Relationships will be set up by setup_student_relationships
    pass 