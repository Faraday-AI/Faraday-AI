"""
Workout Models

This module defines workout-related models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, Float, Table, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    WorkoutType,
    ExerciseType,
    ExerciseDifficulty
)
from app.models.physical_education.teacher.models import PhysicalEducationTeacher

# Re-export for backward compatibility
BaseModelMixin = SharedBase
TimestampMixin = TimestampedMixin

class Workout(SharedBase, TimestampedMixin):
    """Model for workouts."""
    __tablename__ = "physical_education_workouts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    workout_name = Column(String, nullable=False)
    workout_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    difficulty_level = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    workout_metadata = Column(JSON, nullable=True)

    # Relationships
    # exercises relationship removed since PhysicalEducationWorkoutExercise now points to health_fitness_workouts
    student_workouts = relationship("StudentWorkout", back_populates="workout")
    performances = relationship("WorkoutPerformance", back_populates="workout")
    sessions = relationship("app.models.physical_education.workout.models.WorkoutSession", back_populates="workout")
    plan_workouts = relationship("app.models.physical_education.workout.models.WorkoutPlanWorkout", back_populates="workout")

class StudentWorkout(SharedBase, TimestampedMixin):
    """Model for student workouts."""
    __tablename__ = "student_workouts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("physical_education_workouts.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assigned_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    workout_metadata = Column(JSON, nullable=True)

    # Relationships
    workout = relationship("app.models.physical_education.workout.models.Workout", back_populates="student_workouts")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="workouts")

class PhysicalEducationWorkoutExercise(SharedBase, TimestampMixin):
    """Model for exercises in workouts."""
    
    __tablename__ = "physical_education_workout_exercises"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("health_fitness_workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    exercise_metadata = Column(JSON, nullable=True)
    
    # Relationships
    # workout relationship removed since it now points to health_fitness_workouts
    exercise = relationship('app.models.physical_education.exercise.models.Exercise')

class WorkoutPerformance(SharedBase, TimestampMixin):
    """Model for tracking workout performances."""
    __tablename__ = "workout_performances"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey("physical_education_workouts.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    performance_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Float)
    calories_burned = Column(Float)
    completed_exercises = Column(Integer)
    performance_metadata = Column(JSON)  # Renamed from metadata
    notes = Column(Text)
    
    # Relationships
    workout = relationship("app.models.physical_education.workout.models.Workout", back_populates="performances")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="workout_performances")

class WorkoutCreate(BaseModel):
    """Pydantic model for creating workouts."""
    
    student_id: int
    workout_date: datetime
    workout_type: str
    duration: Optional[int] = None
    intensity: Optional[str] = None
    calories_burned: Optional[int] = None
    workout_notes: Optional[str] = None
    workout_metadata: Optional[dict] = None

class WorkoutUpdate(BaseModel):
    """Pydantic model for updating workouts."""
    
    workout_date: Optional[datetime] = None
    workout_type: Optional[str] = None
    duration: Optional[int] = None
    intensity: Optional[str] = None
    calories_burned: Optional[int] = None
    workout_notes: Optional[str] = None
    workout_metadata: Optional[dict] = None

class WorkoutResponse(BaseModel):
    """Pydantic model for workout responses."""
    
    id: int
    student_id: int
    workout_date: datetime
    workout_type: str
    duration: Optional[int] = None
    intensity: Optional[str] = None
    calories_burned: Optional[int] = None
    workout_notes: Optional[str] = None
    workout_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutSession(SharedBase, TimestampMixin):
    """Model for tracking workout sessions."""
    __tablename__ = 'workout_sessions'

    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey('physical_education_workouts.id'), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    calories_burned = Column(Integer)
    notes = Column(Text)
    performance_rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workout = relationship('app.models.physical_education.workout.models.Workout', back_populates='sessions')
    student = relationship('app.models.physical_education.student.models.Student', back_populates='workout_sessions', overlaps="health_fitness_workout_sessions")
    teacher = relationship('app.models.core.user.User', back_populates='workout_sessions')

class WorkoutSessionCreate(BaseModel):
    """Pydantic model for creating workout sessions."""
    
    workout_id: int
    student_id: int
    teacher_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    performance_rating: Optional[int] = None

class WorkoutSessionUpdate(BaseModel):
    """Pydantic model for updating workout sessions."""
    
    workout_id: Optional[int] = None
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    performance_rating: Optional[int] = None

class WorkoutSessionResponse(BaseModel):
    """Pydantic model for workout session responses."""
    
    id: int
    workout_id: int
    student_id: int
    teacher_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    performance_rating: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutPlan(SharedBase, TimestampMixin):
    """Model for tracking workout plans."""
    __tablename__ = 'workout_plans'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    frequency = Column(String(50), nullable=False)
    goals = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship('Student', back_populates='workout_plans', overlaps="health_fitness_workout_plans")
    teacher = relationship('app.models.core.user.User', back_populates='workout_plans')
    plan_workouts = relationship('app.models.physical_education.workout.models.WorkoutPlanWorkout', back_populates='plan')

class WorkoutPlanCreate(BaseModel):
    """Pydantic model for creating workout plans."""
    
    name: str
    description: Optional[str] = None
    student_id: int
    teacher_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    frequency: str
    goals: Optional[str] = None
    notes: Optional[str] = None

class WorkoutPlanUpdate(BaseModel):
    """Pydantic model for updating workout plans."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    frequency: Optional[str] = None
    goals: Optional[str] = None
    notes: Optional[str] = None

class WorkoutPlanResponse(BaseModel):
    """Pydantic model for workout plan responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    student_id: int
    teacher_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    frequency: str
    goals: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutPlanWorkout(SharedBase, TimestampMixin):
    """Model for tracking workouts within a plan."""
    __tablename__ = 'workout_plan_workouts'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('workout_plans.id'), nullable=False)
    workout_id = Column(Integer, ForeignKey('physical_education_workouts.id'), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    order = Column(Integer, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plan = relationship('app.models.physical_education.workout.models.WorkoutPlan', back_populates='plan_workouts')
    workout = relationship('app.models.physical_education.workout.models.Workout', back_populates='plan_workouts')

class WorkoutPlanWorkoutCreate(BaseModel):
    """Pydantic model for creating workout plan workouts."""
    
    plan_id: int
    workout_id: int
    day_of_week: str
    order: int
    notes: Optional[str] = None

class WorkoutPlanWorkoutUpdate(BaseModel):
    """Pydantic model for updating workout plan workouts."""
    
    plan_id: Optional[int] = None
    workout_id: Optional[int] = None
    day_of_week: Optional[str] = None
    order: Optional[int] = None
    notes: Optional[str] = None

class WorkoutPlanWorkoutResponse(BaseModel):
    """Pydantic model for workout plan workout responses."""
    
    id: int
    plan_id: int
    workout_id: int
    day_of_week: str
    order: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 