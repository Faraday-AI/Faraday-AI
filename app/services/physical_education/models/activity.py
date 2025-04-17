from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum, Table, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from pydantic import BaseModel, Field, validator
from .class_ import Class
from .activity_category_association import ActivityCategoryAssociation
from .routine import Routine
from .exercise import Exercise

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

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(SQLEnum(ActivityType), nullable=False)
    difficulty_level = Column(SQLEnum(DifficultyLevel), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    equipment_requirements = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    routines = relationship("RoutineActivity", back_populates="activity")
    adaptations = relationship("ActivityAdaptation", back_populates="activity")
    assessments = relationship("SkillAssessment", back_populates="activity")
    exercises = relationship("Exercise", back_populates="activity")
    category_associations = relationship("ActivityCategoryAssociation", back_populates="activity", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Activity {self.name}>"

class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: ActivityType
    difficulty_level: DifficultyLevel
    duration_minutes: int = Field(..., gt=0, le=240)  # Max 4 hours
    equipment_requirements: Optional[List[EquipmentRequirement]] = None

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[ActivityType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_minutes: Optional[int] = Field(None, gt=0, le=240)
    equipment_requirements: Optional[List[EquipmentRequirement]] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v

    @validator('description')
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        return v.strip() if v else v

class ActivityResponse(ActivityBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentActivityPerformance(Base):
    """Model for tracking student performance in specific activities."""
    __tablename__ = "student_activity_performances"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
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

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
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

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
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