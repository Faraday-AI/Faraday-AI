"""
Physical Education Models

This module defines the models for physical education functionality in the Faraday AI system.
"""

from sqlalchemy import Column, String, JSON, Boolean, ForeignKey, DateTime, Integer, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import Optional, Dict, List

from app.models.physical_education.base.base_class import Base
from ...core.base import BaseModel, StatusMixin, MetadataMixin

class ClassStatus(str, enum.Enum):
    """Enum for class status."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Routine(Base):
    """Model for physical education routines."""
    __tablename__ = "physical_education_base_routines"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    routine_type = Column(String, nullable=False)
    duration = Column(Integer, nullable=True)  # in minutes
    routine_metadata = Column(JSON, nullable=True)

    # Relationships
    students = relationship("Student", secondary="student_routines", back_populates="routines")
    performances = relationship("BaseRoutinePerformance", back_populates="routine")

class StudentRoutine(Base):
    """Model for student routine assignments."""
    __tablename__ = "student_routines"
    __table_args__ = {'extend_existing': True}

    routine_id = Column(Integer, ForeignKey("physical_education_routines.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    performance_metrics = Column(JSON, nullable=True)

    # Relationships
    routine = relationship("Routine", back_populates="student_assignments")
    student = relationship("User", back_populates="routine_assignments")

class BaseRoutinePerformance(Base):
    """Model for routine performance tracking."""
    __tablename__ = "physical_education_base_routine_performance"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    routine_id = Column(Integer, ForeignKey("physical_education_routines.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performance_date = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=True)  # in minutes
    performance_metrics = Column(JSON, nullable=True)

    # Relationships
    routine = relationship("Routine", back_populates="performances")
    student = relationship("User", back_populates="routine_performances")
    metrics = relationship("PhysicalEducationPerformanceMetric", back_populates="performance")

class PhysicalEducationPerformanceMetric(Base):
    """Model for physical education performance metrics."""
    __tablename__ = "physical_education_performance_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    performance_id = Column(Integer, ForeignKey("routine_performance.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    metric_metadata = Column(JSON, nullable=True)

    # Relationships
    performance = relationship("BaseRoutinePerformance", back_populates="metrics")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "performance_id": self.performance_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "metric_metadata": self.metric_metadata
        } 