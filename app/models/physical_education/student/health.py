"""
Health Models

This module defines health models for physical education students.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.core.base import CoreBase
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = CoreBase
TimestampMixin = TimestampedMixin

# Remove circular import - use string references instead
# from app.models.physical_education.student.models import Student

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
    student = relationship("Student", back_populates="student_medical_conditions")

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

class HealthMetric(CoreBase):
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
    student = relationship("Student", back_populates="student_health_metrics")
    thresholds = relationship("app.models.physical_education.student.health.HealthMetricThreshold", back_populates="metrics")

class HealthMetricThreshold(CoreBase):
    """Model for health metric thresholds."""
    __tablename__ = "health_metric_thresholds"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey("health_metrics.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    threshold_metadata = Column(JSON, nullable=True)

    # Relationships
    metrics = relationship("app.models.physical_education.student.health.HealthMetric", back_populates="thresholds")

class FitnessGoal(CoreBase):
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
    student = relationship("Student", back_populates="pe_fitness_goals")
    progress = relationship("app.models.physical_education.student.health.FitnessGoalProgress", back_populates="goal")

class FitnessGoalProgress(CoreBase):
    """Model for tracking fitness goal progress."""
    __tablename__ = "physical_education_student_fitness_goal_progress"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey("physical_education_student_fitness_goals.id"), nullable=False)
    current_value = Column(Float, nullable=False)
    progress_date = Column(DateTime, nullable=False)
    progress_metadata = Column(JSON, nullable=True)

    # Relationships
    goal = relationship("app.models.physical_education.student.health.FitnessGoal", back_populates="progress")

class StudentHealthGoalProgress(CoreBase):
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
    student = relationship("Student", back_populates="pe_goal_recommendations")

class StudentHealth(BaseModelMixin, TimestampMixin):
    """Model for student health records."""
    
    __tablename__ = "student_health"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    health_status = Column(String(50))
    health_notes = Column(Text)
    health_metadata = Column(JSON)
    
    # Relationships
    student = relationship("Student", back_populates="student_health") 