"""
Fitness Models

This module defines fitness-related models for physical education.
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

class FitnessAssessment(Base):
    """Model for fitness assessments."""
    __tablename__ = "fitness_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    assessment_type = Column(String, nullable=False)
    assessment_metadata = Column(JSON, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="fitness_assessments")
    metrics = relationship("FitnessMetric", back_populates="assessment")

class FitnessMetric(Base):
    """Model for fitness metrics."""
    __tablename__ = "physical_education_fitness_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("fitness_assessments.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    metric_metadata = Column(JSON, nullable=True)
    
    # Relationships
    assessment = relationship("FitnessAssessment", back_populates="metrics")

class FitnessGoal(Base):
    """Model for fitness goals."""
    __tablename__ = "physical_education_fitness_goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    goal_type = Column(String, nullable=False)
    target_value = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=True)
    goal_metadata = Column(JSON, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="fitness_goals")
    progress = relationship("FitnessGoalProgress", back_populates="goal")

class FitnessGoalProgress(Base):
    """Model for tracking fitness goal progress."""
    __tablename__ = "physical_education_fitness_goal_progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("health_fitness_goals.id"), nullable=False)
    current_value = Column(Float, nullable=False)
    progress_date = Column(DateTime, nullable=False)
    progress_metadata = Column(JSON, nullable=True)
    
    # Relationships
    goal = relationship("FitnessGoal", back_populates="progress")

# Pydantic models for API
class FitnessGoalCreate(BaseModel):
    """Pydantic model for creating fitness goals."""
    
    student_id: str
    goal_type: str
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    start_date: datetime
    target_date: datetime
    notes: Optional[str] = None

class FitnessGoalUpdate(BaseModel):
    """Pydantic model for updating fitness goals."""
    
    goal_type: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    target_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class FitnessGoalResponse(BaseModel):
    """Pydantic model for fitness goal responses."""
    
    id: str
    student_id: str
    goal_type: str
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    start_date: datetime
    target_date: datetime
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 