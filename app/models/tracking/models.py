"""
Tracking Models

This module defines tracking models for physical education activities.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    ProgressType,
    ProgressLevel,
    ProgressStatus,
    ProgressTrigger
)

class ActivityTracking(SharedBase, TimestampedMixin):
    """Model for tracking physical education activities."""
    
    __tablename__ = "activity_tracking"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    tracking_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    tracking_type = Column(Enum(ProgressType, name='tracking_type_enum'), nullable=False)
    tracking_status = Column(Enum(ProgressStatus, name='tracking_status_enum'), nullable=False)
    duration_minutes = Column(Integer)
    intensity_level = Column(Enum(ProgressLevel, name='intensity_level_enum'))
    tracking_notes = Column(Text)
    tracking_metadata = Column(JSON)
    
    # Relationships
    activity = relationship("Activity", back_populates="tracking_records")
    student = relationship("Student", back_populates="activity_tracking")
    metrics = relationship("TrackingMetrics", back_populates="tracking")
    history = relationship("TrackingHistory", back_populates="tracking")

class TrackingMetrics(SharedBase, TimestampedMixin):
    """Model for tracking metrics."""
    
    __tablename__ = "tracking_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, ForeignKey("activity_tracking.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(Float)
    metric_unit = Column(String(20))
    metric_notes = Column(Text)
    metric_metadata = Column(JSON)
    
    # Relationships
    tracking = relationship("ActivityTracking", back_populates="metrics")

class TrackingHistory(SharedBase, TimestampedMixin):
    """Model for tracking history."""
    
    __tablename__ = "tracking_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, ForeignKey("activity_tracking.id"), nullable=False)
    history_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    history_type = Column(String(50), nullable=False)
    history_description = Column(Text)
    history_metadata = Column(JSON)
    
    # Relationships
    tracking = relationship("ActivityTracking", back_populates="history")

class TrackingStatus(SharedBase, TimestampedMixin):
    """Model for tracking status."""
    
    __tablename__ = "tracking_status"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, ForeignKey("activity_tracking.id"), nullable=False)
    status = Column(Enum(ProgressStatus, name='status_enum'), nullable=False)
    status_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status_notes = Column(Text)
    status_metadata = Column(JSON)

# Pydantic models for API
class ActivityTrackingCreate(BaseModel):
    """Pydantic model for creating activity tracking records."""
    
    activity_id: int
    student_id: int
    tracking_type: ProgressType
    tracking_status: ProgressStatus
    duration_minutes: Optional[int] = None
    intensity_level: Optional[ProgressLevel] = None
    tracking_notes: Optional[str] = None
    tracking_metadata: Optional[dict] = None

class ActivityTrackingUpdate(BaseModel):
    """Pydantic model for updating activity tracking records."""
    
    tracking_type: Optional[ProgressType] = None
    tracking_status: Optional[ProgressStatus] = None
    duration_minutes: Optional[int] = None
    intensity_level: Optional[ProgressLevel] = None
    tracking_notes: Optional[str] = None
    tracking_metadata: Optional[dict] = None

class ActivityTrackingResponse(BaseModel):
    """Pydantic model for activity tracking responses."""
    
    id: int
    activity_id: int
    student_id: int
    tracking_date: datetime
    tracking_type: ProgressType
    tracking_status: ProgressStatus
    duration_minutes: Optional[int] = None
    intensity_level: Optional[ProgressLevel] = None
    tracking_notes: Optional[str] = None
    tracking_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 