"""
Student Models

This module defines student models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean, Enum, Date
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.physical_education.pe_enums.pe_types import (
    Gender,
    GradeLevel,
    StudentType,
    FitnessLevel,
    FitnessCategory,
    MetricType,
    MeasurementUnit,
    GoalType,
    GoalCategory,
    GoalTimeframe,
    ActivityLevel,
    GoalStatus
)
from app.models.physical_education.relationships import setup_student_health_profile_relationships

class StudentHealthProfile(SharedBase):
    """Model for student health and fitness data."""
    
    __tablename__ = "student_health"
    __table_args__ = {
        'extend_existing': True,
        'sqlite_autoincrement': True
    }
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(20))
    grade_level = Column(String(20))
    student_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = relationship("app.models.physical_education.student.student.HealthRecord", back_populates="student")
    fitness_assessments = relationship("FitnessAssessment", back_populates="student")
    health_skill_assessments = relationship("StudentHealthSkillAssessment", back_populates="student")
    activity_preferences = relationship("ActivityPreference", back_populates="student")
    adaptation_preferences = relationship("app.models.activity_adaptation.student.activity_student.StudentActivityPreference", back_populates="student")
    activity_performances = relationship("ActivityPerformance", back_populates="student")
    activity_adaptations = relationship("app.models.activity_adaptation.activity.activity_adaptation.ActivityAdaptation", back_populates="student")
    student_activity_adaptations = relationship("app.models.activity_adaptation.student.activity_student.ActivityAdaptation", back_populates="student")
    student_health_fitness_goals = relationship("StudentHealthFitnessGoal", back_populates="student")
    health_thresholds = relationship("app.models.physical_education.student.student.HealthMetricThreshold", back_populates="student")
    
    # Adaptation-related relationships
    adapted_workouts = relationship("app.models.activity_adaptation.exercise.exercise.AdaptedWorkout", back_populates="student")
    adapted_routine_performances = relationship("app.models.activity_adaptation.routine.routine_performance.AdaptedRoutinePerformanceBackup", back_populates="student")

class HealthRecord(SharedBase):
    """Model for student health records."""
    
    __tablename__ = "physical_education_student_student_health_records"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    record_date = Column(DateTime, nullable=False)
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    health_notes = Column(Text)
    health_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentHealthProfile", back_populates="health_records")

class FitnessAssessment(SharedBase):
    """Model for student fitness assessments."""
    
    __tablename__ = "fitness_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    assessment_type = Column(String(50), nullable=False)
    score = Column(Float)
    assessment_notes = Column(Text)
    assessment_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentHealthProfile", back_populates="fitness_assessments")

class StudentHealthSkillAssessment(SharedBase):
    """Model for student health-related skill assessments."""
    
    __tablename__ = "student_health_skill_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    skill_type = Column(String(50), nullable=False)
    skill_level = Column(String(20))
    assessment_notes = Column(Text)
    assessment_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentHealthProfile", back_populates="health_skill_assessments")

class ActivityPreference(SharedBase):
    """Model for student activity preferences."""
    
    __tablename__ = "activity_preferences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    preference_level = Column(Integer)
    preference_reason = Column(String, nullable=True)  # Added for seeding compatibility
    preference_notes = Column(Text)
    preference_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentHealthProfile", back_populates="activity_preferences")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="health_preferences")

class ActivityPerformance(SharedBase):
    """Model for student activity performances."""
    
    __tablename__ = "activity_performances"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    performance_date = Column(DateTime, nullable=False)
    performance_score = Column(Float)
    performance_notes = Column(Text)
    performance_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentHealthProfile", back_populates="activity_performances")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="health_performances")

class HealthMetricThreshold(SharedBase):
    """Model for storing acceptable ranges for health metrics."""
    __tablename__ = "health_metric_thresholds"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    metric_type = Column(Enum(MetricType, name='health_metric_type_enum'), nullable=False)
    min_value = Column(Float)
    max_value = Column(Float)
    threshold_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentHealthProfile", back_populates="health_thresholds")

    def __repr__(self):
        return f"<HealthMetricThreshold {self.metric_type} - {self.min_value} to {self.max_value}>"

class StudentHealthFitnessGoal(SharedBase):
    """Model for student health fitness goals (renamed to avoid conflicts)."""
    __tablename__ = "student_health_fitness_goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_health.id", ondelete="CASCADE"), nullable=False)
    goal_type = Column(Enum(GoalType, name='student_health_fitness_goal_type_enum'), nullable=False)
    category = Column(Enum(GoalCategory, name='student_health_fitness_goal_category_enum'), nullable=False)
    timeframe = Column(Enum(GoalTimeframe, name='student_health_fitness_goal_timeframe_enum'), nullable=False, default=GoalTimeframe.SHORT_TERM)
    description = Column(String(1000), nullable=False)
    target_value = Column(Float, nullable=True)  # Target metric value if applicable
    target_date = Column(DateTime, nullable=False)
    completion_date = Column(DateTime, nullable=True)
    status = Column(Enum(GoalStatus, name='student_health_fitness_goal_status_enum'), nullable=False, default=GoalStatus.NOT_STARTED)
    priority = Column(Integer, default=1)  # 1-5 scale
    notes = Column(Text)
    goal_metadata = Column(JSON)  # Additional goal metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentHealthProfile", back_populates="student_health_fitness_goals")

class StudentHealthGoalProgress(SharedBase):
    """Model for tracking progress towards student health fitness goals (renamed to avoid conflicts)."""
    __tablename__ = "student_health_goal_progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("student_health_fitness_goals.id", ondelete="CASCADE"), nullable=False)
    current_value = Column(Float, nullable=True)  # Current metric value if applicable
    progress_percentage = Column(Float, nullable=False)  # Overall progress (0-100)
    notes = Column(Text)
    is_milestone = Column(Boolean, default=False)
    progress_metadata = Column(JSON)  # Additional progress data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudentHealthGoalRecommendation(SharedBase):
    """Model for student health fitness goal recommendations (renamed to avoid conflicts)."""
    __tablename__ = "student_health_goal_recommendations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("student_health_fitness_goals.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_health.id", ondelete="CASCADE"), nullable=False)
    recommendation_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)  # 1-5 scale
    is_implemented = Column(Boolean, default=False)
    recommendation_data = Column(JSON)  # Additional recommendation data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models for API operations
class StudentCreate(BaseModel):
    """Pydantic model for creating students."""
    
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: Optional[str] = None
    grade_level: Optional[str] = None
    student_metadata: Optional[dict] = None

class StudentUpdate(BaseModel):
    """Pydantic model for updating students."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    grade_level: Optional[str] = None
    student_metadata: Optional[dict] = None

class StudentResponse(BaseModel):
    """Pydantic model for student responses."""
    
    id: int
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: Optional[str] = None
    grade_level: Optional[str] = None
    student_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Initialize relationships
setup_student_health_profile_relationships(StudentHealthProfile) 