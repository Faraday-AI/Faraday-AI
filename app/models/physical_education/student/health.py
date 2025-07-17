"""
Health Models

This module defines health models for physical education students.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

class HealthRecord(BaseModelMixin, TimestampMixin):
    """Model for student health records."""
    
    __tablename__ = "physical_education_student_health_health_records"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    record_date = Column(DateTime, nullable=False)
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    health_notes = Column(Text)
    health_metadata = Column(JSON)
    
    # Relationships
    student = relationship("Student", back_populates="health_records")

class MedicalCondition(BaseModelMixin, TimestampMixin):
    """Model for student medical conditions."""
    
    __tablename__ = "medical_conditions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    condition_name = Column(String(100), nullable=False)
    diagnosis_date = Column(DateTime)
    severity = Column(String(20))
    treatment = Column(Text)
    condition_notes = Column(Text)
    condition_metadata = Column(JSON)
    
    # Relationships
    student = relationship("Student", back_populates="medical_conditions")

class EmergencyContact(BaseModelMixin, TimestampMixin):
    """Model for student emergency contacts."""
    
    __tablename__ = "emergency_contacts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    contact_name = Column(String(100), nullable=False)
    contact_relationship = Column(String(50))
    phone_number = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    contact_notes = Column(Text)
    contact_metadata = Column(JSON)
    
    # Relationships
    student = relationship("Student", back_populates="emergency_contacts")

class HealthRecordCreate(BaseModel):
    """Pydantic model for creating health records."""
    
    student_id: int
    record_date: datetime
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    health_notes: Optional[str] = None
    health_metadata: Optional[dict] = None

class HealthRecordUpdate(BaseModel):
    """Pydantic model for updating health records."""
    
    record_date: Optional[datetime] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    health_notes: Optional[str] = None
    health_metadata: Optional[dict] = None

class HealthRecordResponse(BaseModel):
    """Pydantic model for health record responses."""
    
    id: int
    student_id: int
    record_date: datetime
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    health_notes: Optional[str] = None
    health_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthMetric(Base):
    """Model for student health metrics."""
    __tablename__ = "health_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    recorded_at = Column(DateTime, nullable=False)
    metric_metadata = Column(JSON, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="health_metrics")
    thresholds = relationship("HealthMetricThreshold", back_populates="metrics")

class HealthMetricThreshold(Base):
    """Model for health metric thresholds."""
    __tablename__ = "health_metric_thresholds"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    metric_type = Column(String, nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    threshold_metadata = Column(JSON, nullable=True)

    # Relationships
    metrics = relationship("HealthMetric", back_populates="thresholds")

class FitnessGoal(Base):
    """Model for student fitness goals."""
    __tablename__ = "physical_education_student_fitness_goals"
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
    __tablename__ = "physical_education_student_fitness_goal_progress"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("health_fitness_goals.id"), nullable=False)
    current_value = Column(Float, nullable=False)
    progress_date = Column(DateTime, nullable=False)
    progress_metadata = Column(JSON, nullable=True)

    # Relationships
    goal = relationship("FitnessGoal", back_populates="progress")

class StudentHealthGoalProgress(Base):
    """Model for tracking goal progress."""
    __tablename__ = "student_health_goal_progress"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    current_value = Column(Float, nullable=False)
    progress_date = Column(DateTime, nullable=False)
    progress_metadata = Column(JSON, nullable=True)

    # Relationships
    goal = relationship("Goal", back_populates="progress")

class GoalRecommendation(BaseModelMixin, TimestampMixin):
    """Model for goal recommendations."""
    __tablename__ = "goal_recommendations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    recommendation_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False)
    recommendation_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    student = relationship("Student", back_populates="goal_recommendations")

class StudentHealth(BaseModelMixin, TimestampMixin):
    """Model for student health records."""
    
    # ... existing code ... 