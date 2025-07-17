"""
Activity Plan Models

This module defines activity plan models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
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

class ActivityPlan(SharedBase, TimestampedMixin):
    """Model for activity plans."""
    
    __tablename__ = "activity_plans"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    grade_level = Column(String(50))
    duration = Column(Integer)  # in minutes
    difficulty = Column(String(20))
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)  # Optional for class-wide plans
    plan_metadata = Column(JSON)
    
    # Relationships
    activities = relationship("app.models.physical_education.activity_plan.models.ActivityPlanActivity", back_populates="plan")
    objectives = relationship("ActivityPlanObjective", back_populates="plan")
    classes = relationship("ClassPlan", back_populates="plan")
    student = relationship("Student", back_populates="student_activity_plans")

class ActivityPlanActivity(SharedBase, TimestampedMixin):
    """Model for activities in a plan."""
    
    __tablename__ = "activity_plan_activities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("activity_plans.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    sequence = Column(Integer)
    duration = Column(Integer)  # in minutes
    activity_metadata = Column(JSON)
    
    # Relationships
    plan = relationship("app.models.physical_education.activity_plan.models.ActivityPlan", back_populates="activities")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="plan_activities")

class ActivityPlanObjective(SharedBase, TimestampedMixin):
    """Model for objectives in a plan."""
    
    __tablename__ = "activity_plan_objectives"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("activity_plans.id"), nullable=False)
    objective = Column(Text, nullable=False)
    objective_metadata = Column(JSON)
    
    # Relationships
    plan = relationship("app.models.physical_education.activity_plan.models.ActivityPlan", back_populates="objectives")

class ActivityPlanCreate(BaseModel):
    """Pydantic model for creating activity plans."""
    
    name: str
    description: Optional[str] = None
    grade_level: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    plan_metadata: Optional[dict] = None

class ActivityPlanUpdate(BaseModel):
    """Pydantic model for updating activity plans."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    grade_level: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    plan_metadata: Optional[dict] = None

class ActivityPlanResponse(BaseModel):
    """Pydantic model for activity plan responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    grade_level: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[str] = None
    plan_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClassPlan(SharedBase, TimestampedMixin):
    """Model for class plans."""
    
    __tablename__ = "class_plans"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("physical_education_classes.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("activity_plans.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="SCHEDULED")
    class_plan_metadata = Column(JSON)
    
    # Relationships
    physical_education_class = relationship("PhysicalEducationClass")
    plan = relationship("app.models.physical_education.activity_plan.models.ActivityPlan", back_populates="classes") 