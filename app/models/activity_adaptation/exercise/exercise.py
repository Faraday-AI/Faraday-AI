"""Exercise models for physical education."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from app.models.shared_base import SharedBase
import enum
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.physical_education.activity import Activity
from app.models.physical_education.student.models import Student

class ExerciseType(enum.Enum):
    STRENGTH = "STRENGTH"
    CARDIO = "CARDIO"
    FLEXIBILITY = "FLEXIBILITY"
    BALANCE = "BALANCE"
    COORDINATION = "COORDINATION"
    ENDURANCE = "ENDURANCE"

class ExerciseDifficulty(enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class AdaptedExercise(SharedBase):
    """Model for physical education exercises."""
    __tablename__ = "adapted_exercises"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    exercise_type = Column(SQLEnum(ExerciseType, name='exercise_type_enum'), nullable=False)
    difficulty = Column(SQLEnum(ExerciseDifficulty, name='exercise_difficulty_enum'), nullable=False)
    duration_minutes = Column(Integer)
    equipment_needed = Column(JSON)
    instructions = Column(String, nullable=False)
    target_muscles = Column(JSON)
    benefits = Column(String)
    precautions = Column(String)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Legacy-compatible fields (from service-specific model)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    rest_time_seconds = Column(Integer, nullable=True)
    technique_notes = Column(String, nullable=True)
    intensity = Column(String, nullable=True)
    progression_steps = Column(JSON, nullable=True)
    regression_steps = Column(JSON, nullable=True)

    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", overlaps="activity,exercises", viewonly=True)
    workout_exercises = relationship("AdaptedWorkoutExercise", back_populates="exercise", overlaps="exercise,workout_exercises")

    def __repr__(self):
        return f"<AdaptedExercise {self.name}>"

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    exercise_type: ExerciseType
    difficulty: ExerciseDifficulty
    duration_minutes: int = Field(..., gt=0, le=120)  # Max 2 hours
    equipment_needed: Optional[dict] = None
    instructions: str = Field(..., min_length=1)
    target_muscles: Optional[dict] = None
    benefits: Optional[str] = None
    precautions: Optional[str] = None
    activity_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    exercise_type: Optional[ExerciseType] = None
    difficulty: Optional[ExerciseDifficulty] = None
    duration_minutes: Optional[int] = Field(None, gt=0, le=120)
    equipment_needed: Optional[dict] = None
    instructions: Optional[str] = Field(None, min_length=1)
    target_muscles: Optional[dict] = None
    benefits: Optional[str] = None
    precautions: Optional[str] = None
    activity_id: Optional[int] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

class ExerciseResponse(ExerciseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AdaptedWorkout(SharedBase):
    """Model for tracking student workouts."""
    __tablename__ = "adapted_workouts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    duration_minutes = Column(Integer)
    intensity = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("app.models.physical_education.student.student.StudentHealthProfile", back_populates="adapted_workouts", overlaps="student,adapted_workouts")
    exercises = relationship("AdaptedWorkoutExercise", back_populates="workout", overlaps="workout,exercises")

    def __repr__(self):
        return f"<AdaptedWorkout {self.id} - {self.student_id}>"

class AdaptedWorkoutExercise(SharedBase):
    """Model for tracking exercises within workouts."""
    __tablename__ = "adapted_workout_exercises"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("adapted_workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("adapted_exercises.id"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    duration_minutes = Column(Float)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workout = relationship("AdaptedWorkout", back_populates="exercises")
    exercise = relationship("app.models.activity_adaptation.exercise.exercise.AdaptedExercise", back_populates="workout_exercises", overlaps="exercise,workout_exercises")

    def __repr__(self):
        return f"<AdaptedWorkoutExercise {self.workout_id} - {self.exercise_id}>" 