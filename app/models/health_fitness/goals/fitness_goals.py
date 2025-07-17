from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.physical_education.base.base_class import Base
import enum

class GoalCategory(str, enum.Enum):
    """Categories of fitness goals."""
    CARDIOVASCULAR = "cardiovascular"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    ENDURANCE = "endurance"
    BALANCE = "balance"
    COORDINATION = "coordination"
    SPEED = "speed"
    AGILITY = "agility"
    POWER = "power"
    SPORTS_SPECIFIC = "sports_specific"
    GENERAL_FITNESS = "general_fitness"
    WEIGHT_MANAGEMENT = "weight_management"

class GoalStatus(str, enum.Enum):
    """Status of a fitness goal."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ON_HOLD = "on_hold"
    PLANNED = "planned"

class GoalType(str, enum.Enum):
    """Types of fitness goals."""
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    WEIGHT_MANAGEMENT = "weight_management"
    SKILL_DEVELOPMENT = "skill_development"
    PERFORMANCE = "performance"
    HEALTH = "health"
    REHABILITATION = "rehabilitation"

class GoalTimeframe(str, enum.Enum):
    """Timeframe for fitness goals."""
    SHORT_TERM = "short_term"  # 1-4 weeks
    MEDIUM_TERM = "medium_term"  # 1-3 months
    LONG_TERM = "long_term"  # 3+ months
    ACADEMIC_YEAR = "academic_year"
    CUSTOM = "custom"

class FitnessGoal(Base):
    """Model for student fitness goals."""
    __tablename__ = "health_fitness_goals"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    goal_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    target_value = Column(Float)
    current_value = Column(Float)
    unit = Column(String(20))
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime)
    status = Column(String(20), nullable=False, default=GoalStatus.PLANNED)
    progress = Column(Float, default=0.0)
    is_achieved = Column(Boolean, default=False)
    goal_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships using full module paths to avoid circular imports
    student = relationship("app.models.physical_education.student.models.Student", back_populates="fitness_goals", overlaps="student,fitness_goals")
    recommendations = relationship("app.models.health_fitness.goals.fitness_goals.GoalRecommendation", back_populates="goal", cascade="all, delete-orphan")
    progress_records = relationship("app.models.health_fitness.goals.fitness_goals.FitnessGoalProgressGeneral", back_populates="goal", cascade="all, delete-orphan")
    fitness_progress_records = relationship("app.models.health_fitness.goals.fitness_goals.FitnessGoalProgress", back_populates="fitness_goal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FitnessGoal {self.goal_type} - {self.description[:30]}>"

class FitnessGoalProgressGeneral(Base):
    """Model for tracking progress towards fitness goals (general version)."""
    __tablename__ = "fitness_goal_progress_general"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("health_fitness_goals.id"), nullable=False)
    value = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String, nullable=True)
    is_milestone = Column(Boolean, default=False)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    goal = relationship("FitnessGoal", back_populates="progress_records")

class GoalAdjustment(Base):
    """Model for tracking adjustments to fitness goals."""
    __tablename__ = "goal_adjustments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("health_fitness_goals.id"), nullable=False)
    previous_target = Column(Float, nullable=True)
    new_target = Column(Float, nullable=True)
    previous_date = Column(DateTime, nullable=True)
    new_date = Column(DateTime, nullable=True)
    reason = Column(String, nullable=False)
    adjusted_by = Column(String, nullable=False)  # teacher, system, etc.
    adjustment_date = Column(DateTime, default=datetime.utcnow)
    additional_data = Column(JSON, nullable=True)

    # Relationships
    goal = relationship("FitnessGoal")

class GoalRecommendation(Base):
    """Model for fitness goal recommendations."""
    __tablename__ = "goal_recommendations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal_id = Column(Integer, ForeignKey("health_fitness_goals.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    recommendation_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)
    is_implemented = Column(Boolean, default=False)
    recommendation_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships using full module paths to avoid circular imports
    goal = relationship("app.models.health_fitness.goals.fitness_goals.FitnessGoal", back_populates="recommendations")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="goal_recommendations", overlaps="student,goal_recommendations")

    def __repr__(self):
        return f"<GoalRecommendation {self.recommendation_type} - {self.description[:30]}>"

class FitnessGoalProgress(Base):
    """Model for tracking fitness goal progress."""
    __tablename__ = "fitness_goal_progress_detailed"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    fitness_goal_id = Column(Integer, ForeignKey("health_fitness_goals.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    progress_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress_value = Column(Float, nullable=False)
    progress_percentage = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    evidence = Column(JSON, nullable=True)  # Supporting evidence for progress
    metrics = Column(JSON, nullable=True)  # Detailed metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fitness_goal = relationship("FitnessGoal", back_populates="fitness_progress_records")
    student = relationship("Student", back_populates="fitness_goal_progress")

    def __repr__(self):
        return f"<FitnessGoalProgress {self.fitness_goal_id} - {self.progress_percentage}%>" 