"""
Routine models for physical education.
"""
import warnings
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Table, Text, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import ConfigDict

from app.models.shared_base import SharedBase
from app.models.physical_education.pe_enums.pe_types import (
    RoutineType,
    RoutineStatus,
    ActivityType,
    DifficultyLevel,
    ProgressionLevel
)

# Re-export for backward compatibility
BaseModelMixin = SharedBase
TimestampMixin = None  # We'll use SharedBase which already has timestamps

# Deprecation warning
warnings.warn(
    "app.models.physical_education.routine.models is deprecated. "
    "Use app.models.shared_base instead.",
    DeprecationWarning,
    stacklevel=2
)

class RoutineBase(SharedBase):
    """Base class for routine models."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(RoutineType, name='routine_type_enum'), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel, name='routine_difficulty_level_enum'), nullable=False)
    target_audience = Column(String(100), nullable=False)

class Routine(SharedBase):
    """Model for tracking physical education routines."""
    __tablename__ = "physical_education_routines"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    equipment_needed = Column(JSON, nullable=True)
    target_skills = Column(JSON, nullable=True)
    instructions = Column(Text, nullable=False)
    video_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    difficulty = Column(Enum(DifficultyLevel, name='routine_difficulty_enum'), nullable=False)  # beginner, intermediate, advanced
    created_by = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    class_id = Column(Integer, ForeignKey("physical_education_classes.id", ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="created_regular_routines", lazy="joined")
    class_ = relationship("app.models.physical_education.class_.models.PhysicalEducationClass", back_populates="regular_routines", lazy="joined")
    activities = relationship("app.models.physical_education.routine.models.RoutineActivity", back_populates="routine", cascade="all, delete-orphan", lazy="joined")
    progress = relationship("app.models.physical_education.routine.models.RoutineProgress", back_populates="routine", lazy="joined")
    performances = relationship("app.models.physical_education.routine.models.RoutinePerformance", back_populates="routine", lazy="joined")
    performance_metrics = relationship("app.models.physical_education.routine.routine_performance_models.RoutinePerformanceMetrics", back_populates="routine", lazy="joined")
    exercises = relationship("app.models.physical_education.exercise.models.ExerciseRoutine", back_populates="routine", lazy="joined")

    def __repr__(self):
        return f"<Routine {self.name}>"

class RoutineCreate(SharedBase):
    """Pydantic model for creating routines."""
    __abstract__ = True
    
    name: str
    description: Optional[str] = None
    type: RoutineType
    duration_minutes: int
    difficulty_level: str
    target_audience: str

class RoutineUpdate(SharedBase):
    """Pydantic model for updating routines."""
    __abstract__ = True
    
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[RoutineType] = None
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[str] = None
    target_audience: Optional[str] = None

class RoutineResponse(SharedBase):
    """Pydantic model for routine responses."""
    __abstract__ = True
    
    id: int
    name: str
    description: Optional[str] = None
    type: RoutineType
    duration_minutes: int
    difficulty_level: str
    target_audience: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoutineActivity(SharedBase):
    """Model for tracking activities within routines."""
    __tablename__ = "routine_activities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("physical_education_routines.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    duration_minutes = Column(Float)
    notes = Column(Text)
    
    # Relationships
    routine = relationship("Routine", back_populates="activities")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="routine_activities")

    def __repr__(self):
        return f"<RoutineActivity routine_id={self.routine_id} activity_id={self.activity_id} order={self.sequence_order}>"

class RoutinePerformance(SharedBase):
    """Model for tracking routine performance."""
    __tablename__ = 'routine_performances'

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey('physical_education_routines.id'), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    completion_time = Column(Float, nullable=False)
    energy_level = Column(Integer, nullable=False)  # 1-10 scale
    difficulty_rating = Column(Integer, nullable=False)  # 1-10 scale
    notes = Column(Text)

    # Relationships
    routine = relationship('Routine', back_populates='performances')
    student = relationship('app.models.physical_education.student.models.Student', back_populates='routine_performances')

class RoutineProgress(SharedBase):
    """Model for routine progress."""
    __tablename__ = "routine_progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    routine_id = Column(Integer, ForeignKey("physical_education_routines.id"), nullable=False)
    progress_date = Column(DateTime, nullable=False)
    progress_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    student = relationship("Student", back_populates="routine_progress")
    routine = relationship("Routine", back_populates="progress")
    metrics = relationship("RoutineMetric", back_populates="progress")

class RoutineMetric(SharedBase):
    """Model for routine metrics."""
    __tablename__ = "routine_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("routine_progress.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float)
    unit = Column(String(20))
    metric_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    progress = relationship("RoutineProgress", back_populates="metrics") 