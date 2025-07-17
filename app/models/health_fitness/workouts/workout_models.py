from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
import enum

class WorkoutType(str, enum.Enum):
    """Types of workouts."""
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    HIIT = "hiit"
    CROSSFIT = "crossfit"
    YOGA = "yoga"
    PILATES = "pilates"
    SPORTS = "sports"
    RECOVERY = "recovery"
    CUSTOM = "custom"

class WorkoutIntensity(str, enum.Enum):
    """Workout intensity levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"

class WorkoutStatus(str, enum.Enum):
    """Status of a workout."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

class HealthFitnessWorkoutSession(SharedBase):
    """Model for workout sessions."""
    __tablename__ = "health_fitness_workout_models"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    workout_type = Column(Enum(WorkoutType), nullable=False)
    intensity = Column(Enum(WorkoutIntensity), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float)
    status = Column(Enum(WorkoutStatus), default=WorkoutStatus.PLANNED)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    notes = Column(Text)
    workout_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="workouts")
    exercises = relationship("HealthFitnessWorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
    metrics = relationship("WorkoutMetric", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HealthFitnessWorkoutSession {self.workout_type} - {self.start_time}>"

class HealthFitnessWorkoutExercise(SharedBase):
    """Model for exercises within a workout."""
    __tablename__ = "health_fitness_workout_exercises"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False)
    exercise_name = Column(String(100), nullable=False)
    sets = Column(Integer)
    reps = Column(Integer)
    duration_seconds = Column(Integer)
    weight = Column(Float)
    rest_seconds = Column(Integer)
    order = Column(Integer, nullable=False)
    notes = Column(Text)
    exercise_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout = relationship("HealthFitnessWorkoutSession", back_populates="exercises")

class WorkoutMetric(SharedBase):
    """Model for tracking workout metrics."""
    __tablename__ = "workout_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text)
    metric_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout = relationship("HealthFitnessWorkoutSession", back_populates="metrics") 