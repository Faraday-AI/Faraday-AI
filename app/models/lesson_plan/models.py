"""
Lesson Plan Models

This module defines lesson plan models for physical education.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    DifficultyLevel
)
from app.models.physical_education.activity.models import Activity
from app.models.physical_education.class_.models import PhysicalEducationClass

class LessonPlan(SharedBase, TimestampedMixin):
    """Model for lesson plans."""
    
    __tablename__ = "pe_lesson_plans"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    grade_level = Column(String(50))
    duration = Column(Integer)  # in minutes
    difficulty = Column(String(20))
    class_id = Column(Integer, ForeignKey("physical_education_classes.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    lesson_metadata = Column(JSON)
    
    # Relationships
    activities = relationship("LessonPlanActivity", back_populates="lesson_plan")
    lesson_objectives = relationship("LessonPlanObjective", back_populates="lesson_plan")
    physical_education_class = relationship("PhysicalEducationClass", back_populates="lesson_plans")
    teacher = relationship("User", back_populates="lesson_plans")

class LessonPlanActivity(SharedBase, TimestampedMixin):
    """Model for activities in a lesson plan."""
    
    __tablename__ = "lesson_plan_activities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_plan_id = Column(Integer, ForeignKey("pe_lesson_plans.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    sequence = Column(Integer)
    duration = Column(Integer)  # in minutes
    is_completed = Column(Boolean, default=False, nullable=False)
    activity_metadata = Column(JSON)
    
    # Relationships
    lesson_plan = relationship("app.models.lesson_plan.models.LessonPlan", back_populates="activities")
    activity = relationship("Activity", back_populates="lesson_plan_activities")

class LessonPlanObjective(SharedBase, TimestampedMixin):
    """Model for objectives in a lesson plan."""
    
    __tablename__ = "lesson_plan_objectives"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_plan_id = Column(Integer, ForeignKey("pe_lesson_plans.id"), nullable=False)
    objective = Column(Text, nullable=False)
    objective_metadata = Column(JSON)
    
    # Relationships
    lesson_plan = relationship("app.models.lesson_plan.models.LessonPlan", back_populates="lesson_objectives")

# Pydantic models for API
class LessonPlanCreate(BaseModel):
    """Pydantic model for creating lesson plans."""
    
    title: str
    description: Optional[str] = None
    grade_level: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    class_id: Optional[int] = None
    teacher_id: Optional[int] = None
    lesson_metadata: Optional[dict] = None

class LessonPlanUpdate(BaseModel):
    """Pydantic model for updating lesson plans."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    grade_level: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    class_id: Optional[int] = None
    teacher_id: Optional[int] = None
    lesson_metadata: Optional[dict] = None

class LessonPlanResponse(BaseModel):
    """Pydantic model for lesson plan responses."""
    
    id: int
    title: str
    description: Optional[str] = None
    grade_level: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    class_id: Optional[int] = None
    teacher_id: Optional[int] = None
    is_completed: bool
    lesson_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 