"""
Progress tracking models for monitoring long-term student development.

This module contains models for tracking student progress across multiple
activities, skills, and fitness metrics over time.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin
from app.models.student import Student

class ProgressBaseModel(BaseModel, TimestampedMixin, MetadataMixin):
    """Base model for progress tracking with metadata, audit, and validation support."""
    
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

class Progress(ProgressBaseModel, StatusMixin):
    """Model for tracking long-term student progress."""
    
    __tablename__ = "progress"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    tracking_period = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=True)
    progress_metrics = Column(JSON, nullable=False)
    baseline_data = Column(JSON, nullable=False)
    current_data = Column(JSON, nullable=False)
    improvement_rate = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    
    # Additional comprehensive tracking fields
    fitness_metrics = Column(JSON, nullable=True)  # Detailed fitness measurements
    skill_assessments = Column(JSON, nullable=True)  # Skill-specific assessments
    attendance_record = Column(JSON, nullable=True)  # Attendance and participation
    goals_progress = Column(JSON, nullable=True)  # Progress towards goals
    challenges_faced = Column(JSON, nullable=True)  # Documented challenges
    support_provided = Column(JSON, nullable=True)  # Support and interventions
    next_evaluation_date = Column(DateTime, nullable=True)
    is_on_track = Column(Boolean, default=True)
    
    # Performance indicators
    strength_score = Column(Float, nullable=True)
    endurance_score = Column(Float, nullable=True)
    flexibility_score = Column(Float, nullable=True)
    coordination_score = Column(Float, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="progress")
    goals = relationship("app.models.health_fitness.progress.progress_tracking.ProgressGoal", back_populates="progress", cascade="all, delete-orphan")
    notes = relationship("HealthFitnessProgressNote", back_populates="progress", cascade="all, delete-orphan")

class ProgressGoal(ProgressBaseModel, NamedMixin, StatusMixin):
    """Model for tracking specific progress goals."""
    
    __tablename__ = "progress_goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    progress_id = Column(Integer, ForeignKey("progress.id"), nullable=False, index=True)
    goal_type = Column(String, nullable=False)  # e.g., "fitness", "skill", "attendance"
    target_date = Column(DateTime, nullable=False)
    achieved_date = Column(DateTime, nullable=True)
    target_metrics = Column(JSON, nullable=False)
    achieved_metrics = Column(JSON, nullable=True)
    priority = Column(String, nullable=False, default="medium")
    difficulty_level = Column(String, nullable=False, default="moderate")
    prerequisites = Column(JSON, nullable=True)
    next_steps = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    progress = relationship("Progress", back_populates="goals")

class HealthFitnessProgressNote(ProgressBaseModel, StatusMixin):
    """Model for generating comprehensive progress notes."""
    
    __tablename__ = "health_fitness_progress_notes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    progress_id = Column(Integer, ForeignKey("progress.id"), nullable=False, index=True)
    note_date = Column(DateTime, default=datetime.utcnow, index=True)
    note_type = Column(String, nullable=False)
    note_period = Column(String, nullable=False)  # e.g., "weekly", "monthly", "quarterly"
    note_data = Column(JSON, nullable=False)
    
    # Detailed reporting fields
    performance_summary = Column(JSON, nullable=False)
    achievement_highlights = Column(JSON, nullable=True)
    areas_for_improvement = Column(JSON, nullable=True)
    recommendations = Column(String, nullable=True)
    next_steps = Column(String, nullable=True)
    parent_feedback = Column(String, nullable=True)
    teacher_feedback = Column(String, nullable=True)
    student_feedback = Column(String, nullable=True)
    
    # Analysis fields
    trend_analysis = Column(JSON, nullable=True)
    comparative_metrics = Column(JSON, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    success_factors = Column(JSON, nullable=True)
    
    # Relationships
    progress = relationship("Progress", back_populates="notes") 