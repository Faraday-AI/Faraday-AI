"""
Activity Models

This module defines activity-related models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum, Float, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    ActivityCategoryType,
    ActivityDifficulty,
    ActivityStatus,
    ActivityFormat,
    ActivityGoal,
    ProgressionLevel,
    PerformanceLevel,
    EquipmentRequirement
)

class Activity(SharedBase):
    """Model for physical education activities."""
    __tablename__ = 'activities'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    difficulty_level = Column(String(20))
    duration = Column(Integer)  # in minutes
    equipment_needed = Column(Text)
    safety_notes = Column(Text)
    type = Column(SQLEnum(ActivityType, name='activity_type_enum'))  # Activity type
    
    # Enhanced fields for better activity tracking
    calories_burn_rate = Column(Float)  # calories burned per minute
    target_muscle_groups = Column(Text)  # primary muscle groups targeted
    
    # Additional columns specific to Activity
    category = Column(SQLEnum(ActivityCategoryType, name='activity_category_enum'))
    format = Column(SQLEnum(ActivityFormat, name='activity_format_enum'))
    goal = Column(SQLEnum(ActivityGoal, name='activity_goal_enum'))
    status = Column(SQLEnum(ActivityStatus, name='activity_status_enum'))
    
    # Relationships
    performances = relationship("StudentActivityPerformance", back_populates="activity", cascade="all, delete-orphan")
    health_performances = relationship("app.models.physical_education.student.student.ActivityPerformance", back_populates="activity", cascade="all, delete-orphan")
    preferences = relationship("app.models.physical_education.activity.models.StudentActivityPreference", back_populates="activity", cascade="all, delete-orphan")
    health_preferences = relationship("app.models.physical_education.student.student.ActivityPreference", back_populates="activity", cascade="all, delete-orphan")
    progressions = relationship("app.models.activity_adaptation.student.activity_student.ActivityProgression", back_populates="activity", cascade="all, delete-orphan")
    activity_progressions = relationship("app.models.physical_education.activity.models.ActivityProgression", back_populates="activity", cascade="all, delete-orphan")
    routine_activities = relationship("app.models.physical_education.routine.models.RoutineActivity", back_populates="activity", cascade="all, delete-orphan")
    adapted_routine_activities = relationship("app.models.activity_adaptation.routine.routine.AdaptedRoutineActivity", back_populates="activity", cascade="all, delete-orphan")
    assessments = relationship("ActivityAssessment", back_populates="activity", cascade="all, delete-orphan")
    general_assessments = relationship("app.models.assessment.GeneralAssessment", back_populates="activity", overlaps="activity,assessments")
    adaptations = relationship("app.models.physical_education.activity_adaptation.activity_adaptation.ActivityAdaptation", back_populates="activity", cascade="all, delete-orphan")
    pe_adaptations = relationship("app.models.activity_adaptation.activity.activity_adaptation.ActivityAdaptation", back_populates="activity", cascade="all, delete-orphan")
    student_adaptations = relationship("app.models.activity_adaptation.student.activity_student.ActivityAdaptation", back_populates="activity", cascade="all, delete-orphan")
    safety_incidents = relationship("app.models.physical_education.safety.models.SafetyIncident", back_populates="activity", cascade="all, delete-orphan")
    safety_checklists = relationship("app.models.physical_education.safety.models.SafetyChecklist", back_populates="activity", cascade="all, delete-orphan")
    safety_alerts = relationship("app.models.physical_education.safety.models.SafetyAlert", back_populates="activity", cascade="all, delete-orphan")
    risk_assessments = relationship("app.models.physical_education.safety.models.RiskAssessment", back_populates="activity", cascade="all, delete-orphan")
    exercises = relationship("app.models.physical_education.exercise.models.Exercise", back_populates="activity", overlaps="activity,exercises", viewonly=True)
    adapted_exercises = relationship("app.models.activity_adaptation.exercise.exercise.AdaptedExercise", overlaps="activity,adapted_exercises", viewonly=True)
    category_associations = relationship("app.models.activity_adaptation.categories.associations.ActivityCategoryAssociation", back_populates="activity", cascade="all, delete-orphan")
    categories = relationship(
        "app.models.activity_adaptation.categories.activity_categories.ActivityCategory",
        secondary="activity_category_associations",
        back_populates="activities",
        viewonly=True
    )
    activity_plans = relationship("app.models.activity_adaptation.activity.activity.ActivityPlanActivity", back_populates="activity")
    plan_activities = relationship("app.models.physical_education.activity_plan.models.ActivityPlanActivity", back_populates="activity")
    skill_progress = relationship("app.models.skill_assessment.assessment.assessment.SkillProgress", back_populates="activity")
    assessment_metrics = relationship("app.models.skill_assessment.assessment.assessment.AssessmentMetrics", back_populates="activity")
    movement_analyses = relationship("app.models.movement_analysis.analysis.movement_analysis.MovementAnalysis", back_populates="activity", overlaps="activity,movement_analyses")
    circuit_breakers = relationship("app.models.circuit_breaker.CircuitBreaker", back_populates="activity", overlaps="activity,circuit_breakers")
    # Progress relationships will be set up by setup_all_physical_education_relationships() after model initialization
    # This avoids circular import issues during SQLAlchemy mapper configuration
    pass  # Relationships added via setup_all_physical_education_relationships()
    
    # Equipment usage relationship using string reference
    equipment_usage = relationship(
        "EquipmentUsage",
        foreign_keys="EquipmentUsage.activity_id",
        viewonly=True
    )
    
    # Environmental relationships
    environmental_conditions = relationship("EnvironmentalCondition", back_populates="activity")
    environmental_impacts = relationship("ActivityEnvironmentalImpact", back_populates="activity")
    
    # Injury prevention relationships
    prevention_assessments = relationship("app.models.physical_education.injury_prevention.PreventionAssessment", back_populates="activity")
    injury_preventions = relationship("app.models.physical_education.injury_prevention.ActivityInjuryPrevention", back_populates="activity")
    
    # Safety relationships
    risk_assessments = relationship("app.models.physical_education.safety.models.RiskAssessment", back_populates="activity", overlaps="activity,risk_assessments")
    skill_assessment_risk_assessments = relationship("app.models.skill_assessment.safety.safety.RiskAssessment", back_populates="activity", overlaps="activity,skill_assessment_risk_assessments")
    safety_alerts = relationship("app.models.physical_education.safety.models.SafetyAlert", back_populates="activity", overlaps="activity,safety_alerts")
    skill_assessment_safety_alerts = relationship("app.models.skill_assessment.safety.safety.SafetyAlert", back_populates="activity", overlaps="activity,skill_assessment_safety_alerts")
    safety = relationship("app.models.skill_assessment.safety.safety.Safety", back_populates="activity", overlaps="activity,safety")
    safety_checks = relationship("app.models.physical_education.safety.models.SafetyCheck", back_populates="activity", overlaps="activity,safety_checks")
    skill_assessment_safety_checks = relationship("app.models.skill_assessment.safety.safety.SafetyCheck", back_populates="activity", overlaps="activity,skill_assessment_safety_checks")
    tracking_records = relationship("app.models.tracking.models.ActivityTracking", back_populates="activity")
    lesson_plan_activities = relationship("app.models.lesson_plan.models.LessonPlanActivity", back_populates="activity")
    progress_records = relationship("app.models.progress.progress_model.ProgressModel", back_populates="activity")
    progress_goals = relationship("app.models.progress.progress_goal.ProgressGoal", back_populates="activity")
    
    def __repr__(self):
        return f"<Activity {self.name} - {self.difficulty_level}>"

class ActivityCreate(BaseModel):
    """Pydantic model for creating activities."""
    
    name: str
    description: Optional[str] = None
    type: ActivityType
    difficulty: ActivityDifficulty
    progression_level: Optional[ProgressionLevel] = None
    duration_minutes: Optional[int] = None
    equipment_needed: Optional[dict] = None
    instructions: Optional[dict] = None
    activity_metadata: Optional[dict] = None

class ActivityUpdate(BaseModel):
    """Pydantic model for updating activities."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ActivityType] = None
    difficulty: Optional[ActivityDifficulty] = None
    progression_level: Optional[ProgressionLevel] = None
    duration_minutes: Optional[int] = None
    equipment_needed: Optional[dict] = None
    instructions: Optional[dict] = None
    activity_metadata: Optional[dict] = None

class ActivityResponse(BaseModel):
    """Pydantic model for activity responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    type: ActivityType
    difficulty: ActivityDifficulty
    progression_level: Optional[ProgressionLevel] = None
    duration_minutes: Optional[int] = None
    equipment_needed: Optional[dict] = None
    instructions: Optional[dict] = None
    activity_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StudentActivityPerformance(SharedBase):
    """Model for tracking student performance in activities."""
    
    __tablename__ = "student_activity_performances"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    performance_level = Column(SQLEnum(PerformanceLevel, name='performance_level_enum'), nullable=False)
    score = Column(Float)
    completion_time = Column(Integer)  # in seconds
    attempts = Column(Integer, nullable=False, default=1)
    notes = Column(Text)
    feedback = Column(JSON, nullable=True)
    performance_metadata = Column(JSON, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="activity_performances")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="performances")

class StudentActivityPreference(SharedBase):
    """Model for tracking student preferences for activities."""
    
    __tablename__ = "pe_activity_preferences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    preference_score = Column(Float)  # 0-1 scale
    preference_level = Column(Integer, nullable=False)  # 1-5 scale
    notes = Column(Text)
    preference_metadata = Column(JSON, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="pe_activity_preferences")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="preferences")

class ActivityAssessment(SharedBase):
    """Model for tracking activity assessments."""
    
    __tablename__ = "activity_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    assessment_type = Column(String(50), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performance_level = Column(SQLEnum(PerformanceLevel, name='assessment_performance_level_enum'), default=PerformanceLevel.SATISFACTORY)
    feedback = Column(Text)
    recommendations = Column(Text)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="assessments")
    assessor = relationship("User", back_populates="conducted_assessments")

class ActivityProgression(SharedBase):
    """Model for tracking activity progression levels."""
    
    __tablename__ = "activity_progressions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    level = Column(SQLEnum(ProgressionLevel, name='progression_level_enum'), nullable=False)
    current_level = Column(SQLEnum(ProgressionLevel, name='current_progression_level_enum'), nullable=False)
    requirements = Column(Text)
    next_level_id = Column(Integer, ForeignKey("activity_progressions.id"))
    improvement_rate = Column(Float, default=0.0)  # Rate of improvement (0-1 scale)
    last_assessment_date = Column(DateTime, nullable=True)  # Date of last assessment
    next_assessment_date = Column(DateTime, nullable=True)  # Date of next scheduled assessment
    start_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    progression_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="activity_progressions")
    student = relationship("Student", back_populates="activity_progressions") 