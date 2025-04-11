from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum, Table, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

# Import models to avoid circular imports
from app.services.physical_education.models.class_ import Class

# Enums for activity types
class ActivityType(str, enum.Enum):
    WARM_UP = "warm_up"
    SKILL_DEVELOPMENT = "skill_development"
    FITNESS_TRAINING = "fitness_training"
    GAME = "game"
    COOL_DOWN = "cool_down"

class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class EquipmentRequirement(str, enum.Enum):
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    EXTENSIVE = "extensive"

class ActivityCategory(str, enum.Enum):
    CARDIOVASCULAR = "cardiovascular"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    COORDINATION = "coordination"
    BALANCE = "balance"
    AGILITY = "agility"
    SPEED = "speed"
    ENDURANCE = "endurance"

# Association table for activity categories
activity_category_association = Table(
    'activity_category_association',
    Base.metadata,
    Column('activity_id', String, ForeignKey('activities.id')),
    Column('category', String)
)

class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    equipment_required = Column(SQLEnum(EquipmentRequirement), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    instructions = Column(String, nullable=False)
    safety_notes = Column(String, nullable=False)
    variations = Column(JSON, default=list)
    modifications = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exercises = relationship("Exercise", back_populates="activity", cascade="all, delete-orphan")
    routines = relationship("RoutineActivity", back_populates="activity")
    safety_incidents = relationship("SafetyIncident", back_populates="activity", cascade="all, delete-orphan")
    risk_assessment = relationship("RiskAssessment", back_populates="activity", uselist=False, cascade="all, delete-orphan")
    activity_performances = relationship("StudentActivityPerformance", back_populates="activity", cascade="all, delete-orphan")
    progressions = relationship("ActivityProgression", back_populates="activity", cascade="all, delete-orphan")
    plan_activities = relationship("ActivityPlanActivity", back_populates="activity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Activity {self.name}>"

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    rest_time_seconds = Column(Integer, nullable=False)
    technique_notes = Column(String, nullable=False)
    progression_steps = Column(JSON, default=list)
    regression_steps = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity = relationship("Activity", back_populates="exercises")

    def __repr__(self):
        return f"<Exercise {self.name}>"

class Routine(Base):
    """Model for activity routines."""
    __tablename__ = "routines"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    class_id = Column(String, ForeignKey("classes.id"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    focus_areas = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_ = relationship("Class", back_populates="routines")
    activities = relationship("RoutineActivity", back_populates="routine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Routine {self.name}>"

class RoutineActivity(Base):
    """Model for activities in a routine."""
    __tablename__ = "routine_activities"

    id = Column(String, primary_key=True)
    routine_id = Column(String, ForeignKey("routines.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    order = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    activity_type = Column(String, nullable=False)  # warm_up, main, cool_down
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    routine = relationship("Routine", back_populates="activities")
    activity = relationship("Activity", back_populates="routines")

    def __repr__(self):
        return f"<RoutineActivity {self.routine_id} - {self.activity_id}>"

class StudentActivityPerformance(Base):
    """Model for tracking student performance in specific activities."""
    __tablename__ = "student_activity_performances"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    score = Column(Float, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="activity_performances")
    activity = relationship("Activity", back_populates="activity_performances")

    def __repr__(self):
        return f"<StudentActivityPerformance {self.student_id} - {self.activity_id}>"

class StudentActivityPreference(Base):
    """Model for tracking student preferences for activities."""
    __tablename__ = "student_activity_preferences"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    preference_score = Column(Float, nullable=False, default=0.5)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="activity_preferences")

    def __repr__(self):
        return f"<StudentActivityPreference {self.student_id} - {self.activity_type}>"

class ActivityProgression(Base):
    """Model for tracking student progression in activities."""
    __tablename__ = "activity_progressions"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    current_level = Column(SQLEnum(DifficultyLevel), nullable=False)
    improvement_rate = Column(Float, nullable=False, default=0.0)
    last_assessment_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="activity_progressions")
    activity = relationship("Activity", back_populates="progressions")

    def __repr__(self):
        return f"<ActivityProgression {self.student_id} - {self.activity_id}>"

class ActivityPlan(Base):
    """Model for student activity plans."""
    __tablename__ = "activity_plans"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="activity_plans")
    activities = relationship("ActivityPlanActivity", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ActivityPlan {self.name} - {self.student_id}>"

class ActivityPlanActivity(Base):
    """Model for activities in a student's activity plan."""
    __tablename__ = "activity_plan_activities"

    id = Column(String, primary_key=True)
    plan_id = Column(String, ForeignKey("activity_plans.id"), nullable=False)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plan = relationship("ActivityPlan", back_populates="activities")
    activity = relationship("Activity", back_populates="plan_activities")

    def __repr__(self):
        return f"<ActivityPlanActivity {self.plan_id} - {self.activity_id}>" 