"""
Student Models

This module defines the database models for students.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, JSON, Enum, Table, Float, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin
from app.models.shared_base import SharedBase

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

from app.models.physical_education.pe_enums.pe_types import (
    Gender,
    GradeLevel,
    StudentType,
    FitnessLevel,
    FitnessCategory,
    StudentStatus,
    StudentLevel,
    StudentCategory
)
from app.models.system.relationships.relationships import setup_student_relationships

# Import movement analysis models to ensure they're registered with SQLAlchemy
from app.models.physical_education.movement_analysis import movement_models

# Import goal-related classes
# Temporarily commented out to fix mapper initialization issues
# from app.models.physical_education.nutrition.models import NutritionGoal, PhysicalEducationNutritionLog, PhysicalEducationNutritionRecommendation
# from app.models.physical_education.progress.models import ProgressGoal, Progress  # Removed to fix circular import

class Student(SharedBase):
    """Model for student profiles in physical education."""
    __tablename__ = 'students'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(Enum(Gender, name='gender_enum'))
    grade_level = Column(Enum(GradeLevel, name='grade_level_enum'), nullable=False)
    status = Column(Enum(StudentStatus, name='student_status_enum'), default=StudentStatus.ACTIVE)
    level = Column(Enum(StudentLevel, name='student_level_enum'), default=StudentLevel.BEGINNER)
    category = Column(Enum(StudentCategory, name='student_category_enum'), default=StudentCategory.REGULAR)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    medical_conditions = Column(Text)
    emergency_contact = Column(String(100))
    
    # Parent/Guardian information
    parent_name = Column(String(100))
    parent_phone = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships will be set up by setup_student_relationships
    avatar_customizations = relationship("StudentAvatarCustomization", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("app.models.physical_education.student.models.StudentAttendance", back_populates="student")
    educational_attendance_records = relationship("app.models.educational.classroom.class_.ClassAttendance", back_populates="student")
    educational_classes = relationship("app.models.educational.classroom.class_student.EducationalClassStudent", back_populates="student")
    
    # Exercise-related relationships
    exercise_progress = relationship("app.models.physical_education.exercise.models.ExerciseProgress", back_populates="student")
    exercise_performances = relationship("app.models.physical_education.exercise.models.ExercisePerformance", back_populates="student")
    progress_notes = relationship("app.models.physical_education.exercise.models.ExerciseProgressNote", back_populates="student")
    exercise_progressions = relationship("app.models.physical_education.exercise.models.ExerciseProgression", back_populates="student")
    student_exercise_progress = relationship("app.models.physical_education.exercise.models.StudentExerciseProgress", back_populates="student")
    
    # Workout-related relationships
    workouts = relationship("app.models.physical_education.workout.models.StudentWorkout", back_populates="student")
    workout_performances = relationship("app.models.physical_education.workout.models.WorkoutPerformance", back_populates="student")
    workout_sessions = relationship("app.models.physical_education.workout.models.WorkoutSession", back_populates="student")
    workout_plans = relationship("app.models.physical_education.workout.models.WorkoutPlan", back_populates="student")
    health_fitness_workout_sessions = relationship("app.models.health_fitness.workouts.workout.HealthFitnessWorkoutSession", back_populates="student", overlaps="workout_sessions")
    health_fitness_workout_plans = relationship("app.models.health_fitness.workouts.workout.HealthFitnessWorkoutPlan", back_populates="student", overlaps="workout_plans")
    
    # Health and fitness metric relationships
    health_metrics = relationship("app.models.health_fitness.metrics.health.HealthMetric", back_populates="student", overlaps="pe_health_metrics,student_health_metrics")
    pe_health_metrics = relationship("app.models.physical_education.health.models.HealthMetric", back_populates="student", overlaps="health_metrics,student_health_metrics")
    fitness_health_metrics = relationship("app.models.health_fitness.metrics.health_metrics.HealthMetric", back_populates="student", overlaps="health_metrics,pe_health_metrics,student_health_metrics")
    fitness_metrics = relationship("app.models.health_fitness.metrics.health_metrics.FitnessMetric", back_populates="student")
    fitness_metric_history = relationship("app.models.health_fitness.metrics.health_metrics.FitnessMetricHistory", back_populates="student")
    fitness_health_metric_history = relationship("app.models.health_fitness.metrics.health_metrics.HealthMetricHistory", back_populates="student")
    
    # Health condition relationships
    health_conditions = relationship("app.models.health_fitness.metrics.health.HealthCondition", back_populates="student", overlaps="pe_health_conditions")
    pe_health_conditions = relationship("app.models.physical_education.health.models.HealthCondition", back_populates="student", overlaps="health_conditions")
    
    # Health alert and check relationships
    health_alerts = relationship("app.models.physical_education.health.models.HealthAlert", back_populates="student", overlaps="health_fitness_alerts")
    health_fitness_alerts = relationship("app.models.health_fitness.metrics.health.HealthAlert", back_populates="student", overlaps="health_alerts")
    health_checks = relationship("app.models.physical_education.health.models.HealthCheck", back_populates="student")
    health_fitness_checks = relationship("app.models.health_fitness.metrics.health.HealthCheck", back_populates="student", overlaps="health_checks")
    health_records = relationship("app.models.physical_education.student.health.HealthRecord", back_populates="student")
    student_medical_conditions = relationship("app.models.physical_education.student.health.MedicalCondition", back_populates="student")
    emergency_contacts = relationship("app.models.physical_education.student.health.EmergencyContact", back_populates="student")
    student_health_metrics = relationship("app.models.physical_education.student.health.HealthMetric", back_populates="student", overlaps="health_metrics,pe_health_metrics")
    
    # Goal-related relationships
    goals = relationship("app.models.health_fitness.goals.goal_setting.Goal", back_populates="student")
    goal_progress = relationship("app.models.health_fitness.goals.goal_setting.HealthFitnessGoalProgress", back_populates="student")
    fitness_goals = relationship("app.models.health_fitness.goals.fitness_goals.FitnessGoal", back_populates="student")
    fitness_goal_progress = relationship("app.models.health_fitness.goals.fitness_goals.FitnessGoalProgress", back_populates="student")
    pe_fitness_goals = relationship("app.models.physical_education.student.health.FitnessGoal", back_populates="student")
    goal_recommendations = relationship("app.models.health_fitness.goals.fitness_goals.GoalRecommendation", back_populates="student", overlaps="pe_goal_recommendations")
    pe_goal_recommendations = relationship("app.models.physical_education.student.health.GoalRecommendation", back_populates="student", overlaps="goal_recommendations")
    student_health = relationship("app.models.physical_education.student.health.StudentHealth", back_populates="student")
    nutrition_logs = relationship("app.models.health_fitness.nutrition.nutrition.NutritionLog", back_populates="student")
    nutrition_recommendations = relationship("app.models.health_fitness.nutrition.nutrition.NutritionRecommendation", back_populates="student")
    meals = relationship("app.models.health_fitness.nutrition.nutrition.Meal", back_populates="student")
    # physical_education_nutrition_recommendations = relationship(PhysicalEducationNutritionRecommendation, back_populates="student")
    # physical_education_nutrition_logs = relationship(PhysicalEducationNutritionLog, back_populates="student")
    # physical_education_goals = relationship("app.models.physical_education.goal_setting.PhysicalEducationGoal", back_populates="student")
    nutrition_goals = relationship("app.models.physical_education.nutrition.models.NutritionGoal", back_populates="student")
    # Progress relationships
    progress_goals = relationship("app.models.progress.progress_goal.ProgressGoal", back_populates="student")
    progress_records = relationship("app.models.progress.progress_model.ProgressModel", back_populates="student")
    
    # Routine-related relationships
    routine_performance_metrics = relationship("app.models.physical_education.routine.routine_performance_models.RoutinePerformanceMetrics", back_populates="student")
    routine_performances = relationship("app.models.physical_education.routine.models.RoutinePerformance", back_populates="student")
    
    # Skill assessment relationships
    skill_progress = relationship("app.models.skill_assessment.assessment.assessment.SkillProgress", back_populates="student")
    assessment_metrics = relationship("app.models.skill_assessment.assessment.assessment.AssessmentMetrics", back_populates="student")
    skill_assessments = relationship("app.models.physical_education.skill_assessment.skill_assessment_models.SkillAssessment", back_populates="student")
    
    # Assessment relationships
    assessments = relationship("app.models.assessment.GeneralAssessment", back_populates="student", overlaps="student,assessments")
    general_skill_progress = relationship("app.models.assessment.SkillProgress", back_populates="student", overlaps="student,skill_progress")
    
    # Movement analysis relationships
    movement_analyses = relationship("app.models.physical_education.movement_analysis.models.MovementAnalysis", back_populates="student")
    movement_analysis_records = relationship("MovementAnalysisRecord", back_populates="student")
    
    # Tracking relationships
    activity_tracking = relationship("app.models.tracking.models.ActivityTracking", back_populates="student")
    
    # Planning relationships
    activity_plans = relationship("app.models.planning.models.ActivityPlan", back_populates="student")
    
    # Progress relationships
    progress_records = relationship("app.models.progress.progress_model.ProgressModel", back_populates="student")
    
    # School relationships
    school_enrollments = relationship("app.models.physical_education.schools.relationships.StudentSchoolEnrollment", back_populates="student", lazy="select")
    
    # Activity preference relationships
    activity_preferences = relationship("app.models.physical_education.student.student.ActivityPreference", back_populates="student")
    pe_activity_preferences = relationship("app.models.physical_education.activity.models.StudentActivityPreference", back_populates="student")
    adaptation_preferences = relationship("app.models.activity_adaptation.student.activity_student.StudentActivityPreference", back_populates="student")
    student_activity_adaptations = relationship("app.models.activity_adaptation.student.activity_student.ActivityAdaptation", back_populates="student")

class StudentCreate(BaseModel):
    """Pydantic model for creating student profiles."""
    __allow_unmapped__ = True
    
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: datetime
    gender: Optional[str] = None
    grade_level: str
    status: Optional[StudentStatus] = StudentStatus.ACTIVE
    level: Optional[StudentLevel] = StudentLevel.BEGINNER
    category: Optional[StudentCategory] = StudentCategory.REGULAR
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class StudentUpdate(BaseModel):
    """Pydantic model for updating student profiles."""
    __allow_unmapped__ = True
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    grade_level: Optional[str] = None
    status: Optional[StudentStatus] = None
    level: Optional[StudentLevel] = None
    category: Optional[StudentCategory] = None
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None

class StudentResponse(BaseModel):
    """Pydantic model for student profile responses."""
    __allow_unmapped__ = True
    
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: datetime
    gender: Optional[str] = None
    grade_level: str
    status: StudentStatus
    level: StudentLevel
    category: StudentCategory
    medical_conditions: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthRecord(BaseModelMixin, TimestampMixin):
    """Model for tracking student health records."""
    
    __tablename__ = "physical_education_student_health_records"
    
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), nullable=False)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)
    record_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="LOW")
    restrictions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships will be set up by setup_student_relationships
    pass 

class StudentAttendance(SharedBase):
    """Model for tracking student attendance."""
    
    __tablename__ = "physical_education_attendance"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)  # present, absent, late, excused
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<StudentAttendance(id={self.id}, student_id={self.student_id}, date={self.date}, status={self.status})>"

class StudentAttendanceCreate(BaseModel):
    """Pydantic model for creating student attendance records."""
    __allow_unmapped__ = True
    
    student_id: int
    date: datetime
    status: str
    notes: Optional[str] = None

class StudentAttendanceUpdate(BaseModel):
    """Pydantic model for updating student attendance records."""
    __allow_unmapped__ = True
    
    status: Optional[str] = None
    notes: Optional[str] = None

class StudentAttendanceResponse(BaseModel):
    """Pydantic model for student attendance record responses."""
    __allow_unmapped__ = True
    
    id: int
    student_id: int
    date: datetime
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Initialize relationships
setup_student_relationships(Student) 