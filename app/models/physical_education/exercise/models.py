"""
Exercise Models

This module defines exercise-related models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, Float, Table, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    ExerciseType,
    ExerciseDifficulty
)
from app.models.physical_education.teacher.models import PhysicalEducationTeacher

# Re-export for backward compatibility
BaseModelMixin = SharedBase
TimestampMixin = TimestampedMixin

class ExerciseBaseModel(SharedBase, TimestampMixin):
    """Base class for exercise models."""
    __tablename__ = 'exercise_base'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(ExerciseType, name='exercise_type_enum'), nullable=False)
    difficulty = Column(Enum(ExerciseDifficulty, name='exercise_difficulty_enum'), nullable=False)
    target_muscle_groups = Column(String(100), nullable=False)
    equipment_needed = Column(Text)
    instructions = Column(Text, nullable=False)
    safety_precautions = Column(Text)

class Exercise(SharedBase, TimestampMixin):
    """Model for exercises."""
    __tablename__ = "exercises"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    exercise_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=True)
    muscle_groups = Column(JSON, nullable=True)
    equipment_needed = Column(JSON, nullable=True)
    exercise_metadata = Column(JSON, nullable=True)
    category = Column(String, nullable=False)
    target_muscle_groups = Column(JSON, nullable=True)
    instructions = Column(Text, nullable=False)
    video_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="created_exercises")
    variations = relationship("ExerciseVariation", back_populates="exercise", cascade="all, delete-orphan")
    progressions = relationship("ExerciseProgression", back_populates="exercise", cascade="all, delete-orphan")
    workouts = relationship("ExerciseWorkout", secondary="workout_exercises", back_populates="exercises")
    workout_exercises = relationship("ExerciseWorkoutExercise", back_populates="exercise", overlaps="workouts")
    student_progress = relationship("StudentExerciseProgress", back_populates="exercise")
    performances = relationship("ExercisePerformance", back_populates="exercise")
    progress = relationship("ExerciseProgress", back_populates="exercise")
    routines = relationship("ExerciseRoutine", back_populates="exercise")
    progress_notes = relationship("ExerciseProgressNote", back_populates="exercise")
    techniques = relationship("ExerciseTechnique", back_populates="exercise")
    exercise_videos = relationship("ExerciseVideo", back_populates="exercise")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="exercises", overlaps="activity,exercises", viewonly=True)

class ExerciseVideo(SharedBase, TimestampMixin):
    """Model for exercise videos."""
    
    __tablename__ = "exercise_videos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    video_url = Column(String(200), nullable=False)
    video_type = Column(String(50))
    duration = Column(Integer)  # in seconds
    video_notes = Column(Text)
    video_metadata = Column(JSON)
    
    # Relationships
    exercise = relationship("Exercise", back_populates="exercise_videos")

class ExerciseRoutine(SharedBase, TimestampMixin):
    """Model for exercise routines."""
    __tablename__ = "exercise_routines"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    routine_id = Column(Integer, ForeignKey("physical_education_routines.id"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    duration_minutes = Column(Integer)
    routine_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    exercise = relationship("Exercise", back_populates="routines")
    routine = relationship("app.models.physical_education.routine.models.Routine", back_populates="exercises")

class ExerciseProgress(SharedBase, TimestampMixin):
    """Model for exercise progress."""
    __tablename__ = "exercise_progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    progress_date = Column(DateTime, nullable=False)
    progress_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="exercise_progress")
    exercise = relationship("Exercise", back_populates="progress")
    metrics = relationship("ExerciseMetric", back_populates="progress")

class ExerciseMetric(SharedBase, TimestampMixin):
    """Model for exercise metrics."""
    __tablename__ = "exercise_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    progress_id = Column(Integer, ForeignKey("exercise_progress.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float)
    unit = Column(String(20))
    metric_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    progress = relationship("ExerciseProgress", back_populates="metrics")

class ExerciseCreate(BaseModel):
    """Pydantic model for creating exercises."""
    
    name: str
    description: Optional[str] = None
    exercise_type: str
    difficulty: Optional[str] = None
    target_muscle_group: Optional[str] = None
    equipment_needed: Optional[str] = None
    instructions: Optional[str] = None
    exercise_metadata: Optional[dict] = None

class ExerciseUpdate(BaseModel):
    """Pydantic model for updating exercises."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    exercise_type: Optional[str] = None
    difficulty: Optional[str] = None
    target_muscle_group: Optional[str] = None
    equipment_needed: Optional[str] = None
    instructions: Optional[str] = None
    exercise_metadata: Optional[dict] = None

class ExerciseResponse(BaseModel):
    """Pydantic model for exercise responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    exercise_type: str
    difficulty: Optional[str] = None
    target_muscle_group: Optional[str] = None
    equipment_needed: Optional[str] = None
    instructions: Optional[str] = None
    exercise_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkoutBaseModel(BaseModelMixin, TimestampMixin):
    """Base class for workout models."""
    
    __tablename__ = 'workoutbase'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    difficulty = Column(Enum(ExerciseDifficulty, name='workout_difficulty_enum'), nullable=False)
    target_audience = Column(String(100), nullable=False)

class ExerciseWorkout(SharedBase, TimestampMixin):
    """Model for workout routines."""
    __tablename__ = 'workouts'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    difficulty = Column(Enum(ExerciseDifficulty, name='workout_difficulty_enum'), nullable=False)
    target_audience = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exercises = relationship('Exercise', secondary="workout_exercises", back_populates='workouts', overlaps="workout_exercises")
    workout_exercises = relationship('ExerciseWorkoutExercise', back_populates='workout', overlaps="exercises,workouts")

class WorkoutCreate(BaseModel):
    """Pydantic model for creating workouts."""
    
    name: str
    description: Optional[str] = None
    duration_minutes: int
    difficulty: ExerciseDifficulty
    target_audience: str

class WorkoutUpdate(BaseModel):
    """Pydantic model for updating workouts."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: Optional[ExerciseDifficulty] = None
    target_audience: Optional[str] = None

class WorkoutResponse(BaseModel):
    """Pydantic model for workout responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    duration_minutes: int
    difficulty: ExerciseDifficulty
    target_audience: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExerciseWorkoutExercise(SharedBase, TimestampMixin):
    """Association object for exercises in workouts."""
    __tablename__ = 'workout_exercises'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'), nullable=False)
    exercise_id = Column(Integer, ForeignKey('exercises.id'), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    duration_minutes = Column(Float)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workout = relationship('ExerciseWorkout', back_populates='workout_exercises', overlaps="exercises,workouts")
    exercise = relationship('Exercise', back_populates='workout_exercises', overlaps="exercises,workouts")

    def __repr__(self):
        return f"<ExerciseWorkoutExercise id={self.id} workout_id={self.workout_id} exercise_id={self.exercise_id} order={self.order}>"

class ExerciseVariation(SharedBase, TimestampMixin):
    """Model for tracking exercise variations."""
    __tablename__ = "exercise_variations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=False)
    instructions = Column(Text, nullable=False)
    video_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exercise = relationship("Exercise", back_populates="variations")

class ExercisePerformance(SharedBase, TimestampMixin):
    """Model for tracking exercise performances."""
    
    __tablename__ = "exercise_performances"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    performance_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Float)
    repetitions = Column(Integer)
    sets = Column(Integer)
    weight = Column(Float)
    notes = Column(Text)
    
    # Relationships
    exercise = relationship("Exercise", back_populates="performances")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="exercise_performances")

class ExerciseProgressNote(SharedBase, TimestampMixin):
    """Model for tracking progress notes."""
    __tablename__ = "exercise_progress_notes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    note_date = Column(DateTime, nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="progress_notes")
    exercise = relationship("Exercise", back_populates="progress_notes")

class StudentAvatarCustomization(SharedBase):
    """Model for tracking student avatar customizations."""
    __tablename__ = "student_avatar_customizations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    customization_type = Column(String(50), nullable=False)
    customization_value = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="avatar_customizations")
    avatar = relationship("Avatar", back_populates="student_customizations")

class ExerciseProgression(SharedBase, TimestampMixin):
    __tablename__ = "exercise_progressions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    current_level = Column(Integer, nullable=False, default=1)
    next_level = Column(Integer, nullable=True)
    progress_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exercise = relationship("Exercise", back_populates="progressions")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="exercise_progressions")

class StudentExerciseProgress(SharedBase, TimestampMixin):
    """Model for tracking student exercise progress."""
    __tablename__ = "student_exercise_progress"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    progress_date = Column(DateTime, nullable=False)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    progress_metrics = Column(JSON, nullable=True)

    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="student_exercise_progress")
    exercise = relationship("Exercise", back_populates="student_progress")

class ExerciseTechnique(SharedBase, TimestampMixin):
    """Model for exercise techniques."""
    __tablename__ = "exercise_techniques"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    technique_metadata = Column(JSON, nullable=True)

    # Relationships
    exercise = relationship("Exercise", back_populates="techniques") 