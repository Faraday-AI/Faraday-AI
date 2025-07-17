"""
Goal setting models for managing student fitness and skill objectives.

This module contains models for setting, tracking, and managing student goals
in physical education and fitness.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.shared_base import SharedBase
from app.models.core.base import NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin
from app.models.student import Student
from app.models.activity import Activity

# Association tables
goal_dependencies = Table('goal_dependencies', SharedBase.metadata,
    Column('dependent_goal_id', Integer, ForeignKey('goals.id'), primary_key=True),
    Column('prerequisite_goal_id', Integer, ForeignKey('goals.id'), primary_key=True),
    extend_existing=True
)

class GoalBaseModel(SharedBase, TimestampedMixin, MetadataMixin):
    """Base model for goal tracking with metadata, audit, and validation support."""
    
    __abstract__ = True
    
    # Audit fields
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    audit_trail = Column(JSON, nullable=True, default=list)
    last_audit_at = Column(DateTime, nullable=True)
    audit_status = Column(String, nullable=True)
    
    # Validation fields
    is_valid = Column(Boolean, nullable=False, default=True)
    validation_errors = Column(JSON, nullable=True)
    last_validated_at = Column(DateTime, nullable=True)
    validation_score = Column(Float, nullable=True)
    validation_history = Column(JSON, nullable=True, default=list)
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "audit_trail": self.audit_trail,
            "last_audit_at": self.last_audit_at.isoformat() if self.last_audit_at else None,
            "audit_status": self.audit_status,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "last_validated_at": self.last_validated_at.isoformat() if self.last_validated_at else None,
            "validation_score": self.validation_score,
            "validation_history": self.validation_history
        }

class Goal(SharedBase, NamedMixin, StatusMixin):
    """Model for student fitness and skill goals."""
    
    __tablename__ = "goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    goal_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    target_date = Column(DateTime, nullable=False, index=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    priority = Column(String, nullable=False)
    target_metrics = Column(JSON, nullable=False)
    current_progress = Column(JSON, nullable=True)
    completion_percentage = Column(Float, default=0.0)
    
    # Additional tracking fields
    difficulty_level = Column(String, nullable=False, default="moderate")
    expected_duration = Column(Integer, nullable=True)  # Duration in days
    required_resources = Column(JSON, nullable=True)
    success_criteria = Column(JSON, nullable=False)
    risk_factors = Column(JSON, nullable=True)
    support_needed = Column(JSON, nullable=True)
    
    # Progress tracking
    last_progress_update = Column(DateTime, nullable=True)
    progress_history = Column(JSON, nullable=True)
    blockers = Column(JSON, nullable=True)
    achievements = Column(JSON, nullable=True)
    
    # Motivation and engagement
    motivation_level = Column(String, nullable=True)
    engagement_metrics = Column(JSON, nullable=True)
    reward_system = Column(JSON, nullable=True)
    
    # Goal relationships
    parent_goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    is_template = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="goals")
    milestones = relationship("GoalMilestone", back_populates="goal", cascade="all, delete-orphan")
    activities = relationship("GoalActivity", back_populates="goal", cascade="all, delete-orphan")
    progress_records = relationship("HealthFitnessGoalProgress", back_populates="goal", cascade="all, delete-orphan")
    sub_goals = relationship("Goal", backref="parent", remote_side=[id])
    dependencies = relationship("Goal",
                              secondary=goal_dependencies,
                              primaryjoin=id==goal_dependencies.c.dependent_goal_id,
                              secondaryjoin=id==goal_dependencies.c.prerequisite_goal_id,
                              backref="dependent_goals")

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "student_id": self.student_id,
            "goal_type": self.goal_type,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "priority": self.priority,
            "target_metrics": self.target_metrics,
            "current_progress": self.current_progress,
            "completion_percentage": self.completion_percentage
        }

class GoalMilestone(SharedBase, NamedMixin, StatusMixin):
    """Model for tracking goal milestones."""
    
    __tablename__ = "goal_milestones"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, index=True)
    description = Column(String, nullable=True)
    target_date = Column(DateTime, nullable=False, index=True)
    achieved_date = Column(DateTime, nullable=True)
    metrics = Column(JSON, nullable=False)
    
    # Additional tracking
    priority = Column(String, nullable=False, default="medium")
    difficulty_level = Column(String, nullable=False, default="moderate")
    effort_required = Column(Integer, nullable=True)  # Estimated hours
    prerequisites = Column(JSON, nullable=True)
    validation_criteria = Column(JSON, nullable=True)
    completion_evidence = Column(JSON, nullable=True)
    feedback = Column(String, nullable=True)
    
    # Relationships
    goal = relationship("Goal", back_populates="milestones")

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "goal_id": self.goal_id,
            "description": self.description,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "achieved_date": self.achieved_date.isoformat() if self.achieved_date else None,
            "metrics": self.metrics
        }

class GoalActivity(SharedBase, StatusMixin):
    """Model for activities associated with goals."""
    
    __tablename__ = "goal_activities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False, index=True)
    frequency = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    intensity = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    
    # Activity tracking
    schedule = Column(JSON, nullable=True)  # Detailed schedule information
    progress_metrics = Column(JSON, nullable=True)
    adaptations = Column(JSON, nullable=True)  # Activity modifications
    equipment_needed = Column(JSON, nullable=True)
    space_requirements = Column(JSON, nullable=True)
    safety_considerations = Column(JSON, nullable=True)
    
    # Performance tracking
    performance_history = Column(JSON, nullable=True)
    difficulty_adjustments = Column(JSON, nullable=True)
    feedback_history = Column(JSON, nullable=True)
    
    # Relationships
    goal = relationship("Goal", back_populates="activities")
    activity = relationship("app.models.physical_education.activity.models.Activity")

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "goal_id": self.goal_id,
            "activity_id": self.activity_id,
            "frequency": self.frequency,
            "duration": self.duration,
            "intensity": self.intensity,
            "notes": self.notes
        }

class HealthFitnessGoalProgress(SharedBase, StatusMixin):
    """Model for tracking progress towards goals."""
    
    __tablename__ = "health_fitness_goal_progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    progress_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress_value = Column(Float, nullable=False)
    progress_percentage = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    evidence = Column(JSON, nullable=True)  # Supporting evidence for progress
    metrics = Column(JSON, nullable=True)  # Detailed metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    goal = relationship("Goal", back_populates="progress_records")
    student = relationship("Student", back_populates="goal_progress")

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "goal_id": self.goal_id,
            "student_id": self.student_id,
            "progress_date": self.progress_date.isoformat() if self.progress_date else None,
            "progress_value": self.progress_value,
            "progress_percentage": self.progress_percentage,
            "notes": self.notes,
            "evidence": self.evidence,
            "metrics": self.metrics
        } 