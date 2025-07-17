"""
Movement Analysis Models

This module defines models for movement analysis in physical education.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

from app.models.physical_education.pe_enums.pe_types import (
    PerformanceLevel,
    SkillLevel
)

class MovementAnalysis(BaseModelMixin, TimestampMixin):
    """Model for movement analysis."""
    __tablename__ = "physical_education_movement_analyses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)
    analysis_data = Column(JSON)
    feedback = Column(Text)
    score = Column(Float)
    status = Column(String(20), default="PENDING")
    analysis_metadata = Column(JSON)
    
    # Relationships
    student = relationship("Student", back_populates="movement_analyses")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="movement_analyses")

class MovementMetric(BaseModelMixin, TimestampMixin):
    """Model for movement metrics."""
    __tablename__ = "physical_education_movement_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("movement_analysis_analyses.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float)
    unit = Column(String(20))
    metric_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    analysis = relationship("MovementAnalysis", back_populates="metrics")

class MovementPattern(BaseModelMixin, TimestampMixin):
    """Model for movement patterns."""
    __tablename__ = "physical_education_movement_patterns"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    pattern_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    analyses = relationship("MovementAnalysis", back_populates="pattern")

class MovementAnalysisCreate(BaseModel):
    """Pydantic model for creating movement analyses."""
    
    student_id: int
    activity_id: int
    analysis_type: str
    analysis_data: Optional[dict] = None
    feedback: Optional[str] = None
    score: Optional[float] = None
    status: str = "PENDING"
    analysis_metadata: Optional[dict] = None

class MovementAnalysisUpdate(BaseModel):
    """Pydantic model for updating movement analyses."""
    
    analysis_type: Optional[str] = None
    analysis_data: Optional[dict] = None
    feedback: Optional[str] = None
    score: Optional[float] = None
    status: Optional[str] = None
    analysis_metadata: Optional[dict] = None

class MovementAnalysisResponse(BaseModel):
    """Pydantic model for movement analysis responses."""
    
    id: int
    student_id: int
    activity_id: int
    analysis_type: str
    analysis_data: Optional[dict] = None
    feedback: Optional[str] = None
    score: Optional[float] = None
    status: str
    analysis_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MovementPatternCreate(BaseModel):
    """Pydantic model for creating movement patterns."""
    
    analysis_id: int
    pattern_type: str
    confidence_score: Optional[float] = None
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    pattern_data: Optional[Dict[str, Any]] = None

class MovementPatternUpdate(BaseModel):
    """Pydantic model for updating movement patterns."""
    
    pattern_type: Optional[str] = None
    confidence_score: Optional[float] = None
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    pattern_data: Optional[Dict[str, Any]] = None

class MovementPatternResponse(BaseModel):
    """Pydantic model for movement pattern responses."""
    
    id: int
    analysis_id: int
    pattern_type: str
    confidence_score: Optional[float] = None
    start_frame: Optional[int] = None
    end_frame: Optional[int] = None
    pattern_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MovementFeedback(BaseModelMixin, TimestampMixin):
    """Model for tracking movement feedback."""
    __tablename__ = 'movement_feedback'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    pattern_id = Column(Integer, ForeignKey('movement_patterns.id'), nullable=False)
    feedback_type = Column(String(100), nullable=False)
    feedback_text = Column(Text, nullable=False)
    severity = Column(String(20))
    is_implemented = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    pattern = relationship('MovementPattern', back_populates='feedback')

class MovementFeedbackCreate(BaseModel):
    """Pydantic model for creating movement feedback."""
    
    pattern_id: int
    feedback_type: str
    feedback_text: str
    severity: Optional[str] = None
    is_implemented: bool = False

class MovementFeedbackUpdate(BaseModel):
    """Pydantic model for updating movement feedback."""
    
    feedback_type: Optional[str] = None
    feedback_text: Optional[str] = None
    severity: Optional[str] = None
    is_implemented: Optional[bool] = None

class MovementFeedbackResponse(BaseModel):
    """Pydantic model for movement feedback responses."""
    
    id: int
    pattern_id: int
    feedback_type: str
    feedback_text: str
    severity: Optional[str] = None
    is_implemented: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 