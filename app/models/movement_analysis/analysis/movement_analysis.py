"""
Movement analysis models for tracking and analyzing student movements.

This module contains models for tracking movement patterns, analyzing form,
and providing feedback on physical activities.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.types import Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.shared_base import SharedBase
from app.models.mixins import NamedMixin, StatusMixin, MetadataMixin, TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    AnalysisType,
    ActivityType,
    ActivityDifficulty,
    PerformanceLevel,
    AnalysisStatus,
    ConfidenceLevel,
    MetricType,
    MovementType,
    ExerciseType
)

# Define enum names for PostgreSQL
ANALYSIS_TYPE_ENUM = 'analysis_type_enum'
METRIC_TYPE_ENUM = 'metric_type_enum'
ACTIVITY_TYPE_ENUM = 'activity_type_enum'
DIFFICULTY_LEVEL_ENUM = 'difficulty_level_enum'
FEEDBACK_TYPE_ENUM = 'feedback_type_enum'
FEEDBACK_SEVERITY_ENUM = 'feedback_severity_enum'
SEQUENCE_TYPE_ENUM = 'sequence_type_enum'

class MovementAnalysis(SharedBase, TimestampedMixin, MetadataMixin):
    """Model for analyzing student movements during activities."""
    
    __tablename__ = "movement_analysis_analyses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    analysis_type = Column(SQLEnum(AnalysisType, name=ANALYSIS_TYPE_ENUM), nullable=False)
    movement_data = Column(JSON, nullable=False)  # Raw movement data
    analysis_results = Column(JSON, nullable=False)  # Processed analysis results
    confidence_score = Column(Float, nullable=False)  # Confidence in the analysis
    feedback = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    
    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="movement_analyses", foreign_keys=[student_id])
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="movement_analyses")
    metrics = relationship("app.models.movement_analysis.analysis.movement_analysis.MovementMetrics", back_populates="analysis", overlaps="analysis,metrics")
    sequences = relationship("app.models.movement_analysis.analysis.movement_analysis.MovementSequence", back_populates="analysis", overlaps="analysis,sequences")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "student_id": self.student_id,
            "activity_id": self.activity_id,
            "analysis_type": self.analysis_type,
            "movement_data": self.movement_data,
            "analysis_results": self.analysis_results,
            "confidence_score": self.confidence_score,
            "feedback": self.feedback,
            "recommendations": self.recommendations
        }

class MovementMetrics(SharedBase, TimestampedMixin):
    """Model for storing movement metrics and measurements."""
    
    __tablename__ = "movement_analysis_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("movement_analysis_analyses.id"), nullable=False)
    metric_type = Column(SQLEnum(MetricType, name=METRIC_TYPE_ENUM), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # e.g., "meters", "seconds", "percentage"
    timestamp = Column(DateTime, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Relationships
    analysis = relationship("MovementAnalysis", back_populates="metrics")
    
    def __repr__(self):
        return f"<MovementMetrics {self.metric_type}: {self.value} {self.unit}>"

class MovementPattern(SharedBase, NamedMixin, MetadataMixin):
    """Model for storing recognized movement patterns."""
    
    __tablename__ = "movement_analysis_patterns"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=True)
    pattern_data = Column(JSON, nullable=False)  # Pattern template data
    activity_type = Column(SQLEnum(MovementType, name=ACTIVITY_TYPE_ENUM), nullable=False)
    difficulty_level = Column(SQLEnum(ActivityDifficulty, name=DIFFICULTY_LEVEL_ENUM), nullable=False)
    common_errors = Column(JSON, nullable=True)  # Common mistakes in this pattern
    correction_guidelines = Column(String, nullable=True)
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "description": self.description,
            "pattern_data": self.pattern_data,
            "activity_type": self.activity_type,
            "difficulty_level": self.difficulty_level,
            "common_errors": self.common_errors,
            "correction_guidelines": self.correction_guidelines
        }

class MovementFeedback(SharedBase, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for storing movement-specific feedback."""
    
    __tablename__ = "analysis_movement_feedback"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("movement_analysis_analyses.id"), nullable=False)
    feedback_type = Column(SQLEnum(AnalysisType, name=FEEDBACK_TYPE_ENUM), nullable=False)
    severity = Column(SQLEnum(PerformanceLevel, name=FEEDBACK_SEVERITY_ENUM), nullable=False)
    description = Column(String, nullable=False)
    correction_suggestions = Column(String, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    
    # Relationships
    analysis = relationship("MovementAnalysis")
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "analysis_id": self.analysis_id,
            "feedback_type": self.feedback_type,
            "severity": self.severity,
            "description": self.description,
            "correction_suggestions": self.correction_suggestions,
            "follow_up_required": self.follow_up_required
        }

class MovementSequence(SharedBase, TimestampedMixin):
    """Model for tracking sequences of movements."""
    
    __tablename__ = "movement_sequences"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("movement_analysis_analyses.id"), nullable=False)
    sequence_type = Column(SQLEnum(ExerciseType, name=SEQUENCE_TYPE_ENUM), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    sequence_data = Column(JSON, nullable=False)  # Sequence-specific data
    performance_metrics = Column(JSON)  # Performance metrics for the sequence
    
    # Relationships
    analysis = relationship("MovementAnalysis", back_populates="sequences")
    
    def __repr__(self):
        return f"<MovementSequence {self.sequence_type}>" 