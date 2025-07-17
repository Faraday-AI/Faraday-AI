"""Routine models for physical education."""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Float, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import NamedMixin, StatusMixin, MetadataMixin, TimestampedMixin
from app.models.physical_education.class_.models import PhysicalEducationClass
from app.models.physical_education.activity import Activity
from app.models.physical_education.routine.models import Routine, RoutineActivity
from app.models.physical_education.pe_enums.pe_types import (
    RoutineType,
    RoutineStatus,
    ActivityType,
    DifficultyLevel
)

# Re-export the models
__all__ = [
    'AdaptedRoutine',
    'AdaptedRoutineActivity',
    'AdaptedRoutinePerformance',
    'RoutineActivityBase',
    'RoutineActivityCreate',
    'RoutineActivityUpdate',
    'RoutineActivityResponse',
    'RoutineBase',
    'RoutineCreate',
    'RoutineUpdate',
    'RoutineResponse',
    'RoutineType',
    'RoutineStatus',
    'ActivityType',
    'DifficultyLevel'
]

class AdaptedRoutine(SharedBase, NamedMixin, StatusMixin, MetadataMixin):
    """Model for physical education routines in activity adaptation context."""
    __tablename__ = 'adapted_routines'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey('physical_education_classes.id', ondelete='CASCADE'), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    difficulty = Column(String, nullable=False)  # beginner, intermediate, advanced
    equipment_needed = Column(JSON, nullable=True)
    target_skills = Column(JSON, nullable=True)
    instructions = Column(Text, nullable=False)
    video_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_ = relationship("PhysicalEducationClass", back_populates="adapted_routines")
    creator = relationship("User", back_populates="created_routines")
    activities = relationship("AdaptedRoutineActivity", back_populates="adapted_routine", cascade="all, delete-orphan")
    performances = relationship("AdaptedRoutinePerformance", back_populates="adapted_routine", overlaps="adapted_routine,performances")
    performance_backups = relationship("app.models.activity_adaptation.routine.routine_performance.AdaptedRoutinePerformanceBackup", back_populates="adapted_routine", overlaps="adapted_routine,performances")

    def __repr__(self):
        return f"<AdaptedRoutine {self.name}>"

class AdaptedRoutineActivity(SharedBase, TimestampedMixin):
    """Model for activities within an adapted routine."""
    __tablename__ = 'adapted_routine_activities'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey('adapted_routines.id', ondelete='CASCADE'), nullable=False)
    activity_id = Column(Integer, ForeignKey('activities.id', ondelete='CASCADE'), nullable=False)
    order = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    activity_type = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    # Relationships
    adapted_routine = relationship("AdaptedRoutine", back_populates="activities")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="adapted_routine_activities")

    def __repr__(self):
        return f"<AdaptedRoutineActivity {self.id}>"

class AdaptedRoutinePerformance(SharedBase, TimestampedMixin):
    """Model for tracking performance of adapted routines."""
    __tablename__ = 'adapted_routine_performances'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey('adapted_routines.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    completion_time = Column(Integer, nullable=True)  # in minutes
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    engagement_level = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True)  # Additional performance metrics

    # Relationships
    adapted_routine = relationship("AdaptedRoutine", back_populates="performances", overlaps="adapted_routine,performances")
    student = relationship("Student", back_populates="adapted_routine_performances", overlaps="student,adapted_routine_performances")

    def __repr__(self):
        return f"<AdaptedRoutinePerformance {self.id}>"

class RoutineActivityBase(PydanticBaseModel):
    routine_id: int
    activity_id: int
    order: int
    duration_minutes: int | None = None
    activity_type: ActivityType
    notes: str | None = None

class RoutineActivityCreate(RoutineActivityBase):
    pass

class RoutineActivityUpdate(PydanticBaseModel):
    order: int | None = None
    duration_minutes: int | None = None
    activity_type: ActivityType | None = None
    notes: str | None = None

class RoutineActivityResponse(RoutineActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoutineBase(PydanticBaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    class_id: int
    focus_areas: List[str] | None = None
    status: RoutineStatus = RoutineStatus.DRAFT

class RoutineCreate(RoutineBase):
    pass

class RoutineUpdate(PydanticBaseModel):
    name: str | None = None
    description: str | None = None
    focus_areas: List[str] | None = None
    status: RoutineStatus | None = None

class RoutineResponse(RoutineBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 