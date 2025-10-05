"""Workout models for health and fitness."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean, Float
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.physical_education.pe_enums.pe_types import WorkoutType, DifficultyLevel
from app.models.student import Student

class HealthFitnessExercise(SharedBase):
    """Model for individual exercises."""
    __tablename__ = "health_fitness_exercises"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)  # strength, cardio, flexibility, etc.
    muscle_groups = Column(JSON, nullable=True)  # List of muscle groups targeted
    equipment_needed = Column(JSON, nullable=True)  # List of required equipment
    difficulty_level = Column(SQLEnum(DifficultyLevel, name='exercise_difficulty_enum'), nullable=False)
    instructions = Column(String, nullable=False)
    safety_notes = Column(String, nullable=True)
    modifications = Column(JSON, nullable=True)  # List of possible modifications
    video_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - removed workout_exercises since we use exercises table instead

    def __repr__(self):
        return f"<HealthFitnessExercise {self.name} - {self.category}>"

class HealthFitnessWorkout(SharedBase):
    """Model for workout plans."""
    __tablename__ = "health_fitness_workouts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    workout_type = Column(SQLEnum(WorkoutType, name='workout_type_enum'), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel, name='workout_difficulty_enum'), nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    equipment_needed = Column(JSON, nullable=True)
    target_heart_rate = Column(JSON, nullable=True)
    safety_requirements = Column(JSON, nullable=False)
    modifications_available = Column(Boolean, default=True)
    indoor_outdoor = Column(String, nullable=False)  # "indoor", "outdoor", "both"
    space_required = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exercises = relationship("HealthFitnessWorkoutExercise", back_populates="workout", overlaps="workout,exercises")
    sessions = relationship("HealthFitnessWorkoutSession", back_populates="workout", overlaps="sessions,workout")

    def __repr__(self):
        return f"<HealthFitnessWorkout {self.name} - {self.workout_type}>"

class HealthFitnessWorkoutSession(SharedBase):
    """Model for tracking individual workout sessions."""
    __tablename__ = "health_fitness_workout_sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("health_fitness_workouts.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    performance_data = Column(JSON, nullable=True)  # Heart rate, reps completed, etc.
    difficulty_rating = Column(Integer, nullable=True)  # Student's rating 1-5
    enjoyment_rating = Column(Integer, nullable=True)  # Student's rating 1-5
    notes = Column(String, nullable=True)
    modifications_used = Column(JSON, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout = relationship("HealthFitnessWorkout", back_populates="sessions", overlaps="sessions,workout")
    student = relationship("Student", back_populates="health_fitness_workout_sessions", overlaps="student,workout_sessions")

    def __repr__(self):
        return f"<HealthFitnessWorkoutSession {self.workout_id} - {self.student_id}>"

class HealthFitnessWorkoutPlan(SharedBase):
    """Model for student workout plans."""
    __tablename__ = "health_fitness_workout_plans"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    frequency = Column(Integer, nullable=False)  # workouts per week
    goals = Column(JSON, nullable=False)
    progress_metrics = Column(JSON, nullable=False)
    schedule = Column(JSON, nullable=False)  # Weekly schedule
    adaptations_needed = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="health_fitness_workout_plans", overlaps="student,workout_plans")
    workouts = relationship("HealthFitnessWorkoutPlanWorkout", back_populates="plan", overlaps="plan,plan_workouts")

    def __repr__(self):
        return f"<HealthFitnessWorkoutPlan {self.name} - {self.student_id}>"

class HealthFitnessWorkoutPlanWorkout(SharedBase):
    """Model for associating workouts with workout plans."""
    __tablename__ = "health_fitness_workout_plan_workouts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("health_fitness_workout_plans.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("health_fitness_workouts.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    order = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    plan = relationship("HealthFitnessWorkoutPlan", back_populates="workouts", overlaps="plan,plan_workouts")
    workout = relationship("HealthFitnessWorkout", overlaps="plan_workouts,workout")

    def __repr__(self):
        return f"<HealthFitnessWorkoutPlanWorkout {self.plan_id} - {self.workout_id}>"

class HealthFitnessWorkoutExercise(SharedBase):
    """Model for tracking exercises within workouts."""
    __tablename__ = "health_fitness_workout_exercises"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("health_fitness_workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    duration_minutes = Column(Float)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workout = relationship("HealthFitnessWorkout", back_populates="exercises", overlaps="workout,exercises")
    exercise = relationship("Exercise", back_populates="health_fitness_workout_exercises")
    exercise_sets = relationship("ExerciseSet", back_populates="workout_exercise", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HealthFitnessWorkoutExercise {self.workout_id} - {self.exercise_id}>"

class ExerciseSet(SharedBase):
    """Model for tracking individual sets within exercises."""
    __tablename__ = "exercise_sets"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    workout_exercise_id = Column(Integer, ForeignKey("health_fitness_workout_exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    reps_completed = Column(Integer, nullable=True)
    weight_used = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    distance_meters = Column(Float, nullable=True)
    rest_time_seconds = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    performance_rating = Column(Integer, nullable=True)  # 1-5 scale
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout_exercise = relationship("HealthFitnessWorkoutExercise", back_populates="exercise_sets")

    def __repr__(self):
        return f"<ExerciseSet {self.workout_exercise_id} - Set {self.set_number}>" 