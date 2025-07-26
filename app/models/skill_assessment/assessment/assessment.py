"""Assessment models for physical education."""
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.models.shared_base import SharedBase
from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.core.core_models import AssessmentStatus, CriteriaType, ChangeType
from app.models.physical_education.activity.models import Activity
from app.models.educational.curriculum import Curriculum
import logging
from pathlib import Path
from enum import Enum

class AssessmentType(str, Enum):
    SKILL = "skill"
    FITNESS = "fitness"
    MOVEMENT = "movement"
    BEHAVIORAL = "behavioral"
    PROGRESS = "progress"

class Assessment(SharedBase, TimestampedMixin, StatusMixin):
    """Base model for all types of assessments."""
    __tablename__ = "skill_assessment_assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    curriculum_id = Column(Integer, ForeignKey("curricula.id"), nullable=True)
    assessment_date = Column(TIMESTAMP(timezone=True), nullable=False)
    assessment_type = Column(SQLEnum(AssessmentType, name='assessment_type_enum'), nullable=False)
    score = Column(Float, nullable=True)
    notes = Column(Text)
    assessment_metadata = Column(JSON)

    # Relationships
    # student = relationship("app.models.physical_education.student.models.Student", 
    #                      back_populates="skill_assessment_assessments", 
    #                      foreign_keys=[student_id])
    assessor = relationship("app.models.core.user.User")  # , back_populates="assessments")
    curriculum = relationship("app.models.educational.curriculum.curriculum.Curriculum", back_populates="assessments")

    # Remove the conflicting constraint since we're using enum columns
    __table_args__ = (
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<Assessment {self.id} - {self.assessment_type}>"

class SkillAssessment(SharedBase, TimestampedMixin, StatusMixin):
    """Model for skill assessment data."""
    __tablename__ = "skill_assessment_skill_assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    assessor_notes = Column(Text)
    assessment_date = Column(TIMESTAMP(timezone=True), nullable=False)
    overall_score = Column(Float)
    assessment_metadata = Column(JSON)

    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="skill_assessments", foreign_keys=[student_id])
    activity = relationship("app.models.physical_education.activity.models.Activity")  # , back_populates="skill_assessments")
    results = relationship("app.models.skill_assessment.assessment.assessment.AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")
    history = relationship("app.models.skill_assessment.assessment.assessment.AssessmentHistory", back_populates="assessment", cascade="all, delete-orphan")
    metrics = relationship("app.models.skill_assessment.assessment.assessment.AssessmentMetrics", back_populates="assessment", cascade="all, delete-orphan")

    # Remove the conflicting constraint since we're using enum columns
    __table_args__ = (
        CheckConstraint(
            'overall_score IS NULL OR (overall_score >= 0.0 AND overall_score <= 100.0)',
            name='valid_overall_score'
        ),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<SkillAssessment {self.id} - {self.status}>"

class AssessmentCriteria(SharedBase, NamedMixin, TimestampedMixin):
    """Model for storing assessment criteria."""
    __tablename__ = "skill_assessment_assessment_criteria"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    criteria_type = Column(String(50), nullable=False)
    rubric = Column(JSON, nullable=False)
    weight = Column(Float, nullable=False)
    min_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    parent_id = Column(Integer, ForeignKey('skill_assessment_assessment_criteria.id', ondelete='CASCADE'))

    # Relationships
    sub_criteria = relationship("app.models.skill_assessment.assessment.assessment.AssessmentCriteria", 
                              backref=backref('parent', remote_side=[id]),
                              cascade="all, delete-orphan")
    assessment_results = relationship("app.models.skill_assessment.assessment.assessment.AssessmentResult", back_populates="criteria")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "criteria_type IN ('technical', 'performance', 'progress', 'safety')",
            name='valid_criteria_type'
        ),
        CheckConstraint(
            'weight >= 0.0 AND weight <= 1.0',
            name='valid_weight'
        ),
        CheckConstraint(
            'min_score <= max_score',
            name='valid_score_range'
        ),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<AssessmentCriteria {self.name} - {self.criteria_type}>"

class AssessmentResult(SharedBase, TimestampedMixin):
    """Model for storing assessment results."""
    __tablename__ = "skill_assessment_assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("skill_assessment_skill_assessments.id"), nullable=False)
    criteria_id = Column(Integer, ForeignKey("skill_assessment_assessment_criteria.id"), nullable=False)
    score = Column(Float, nullable=False)
    notes = Column(Text)
    evidence = Column(JSON)

    # Relationships
    assessment = relationship("app.models.skill_assessment.assessment.assessment.SkillAssessment", back_populates="results")
    criteria = relationship("app.models.skill_assessment.assessment.assessment.AssessmentCriteria", back_populates="assessment_results")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            'score >= 0.0 AND score <= 100.0',
            name='valid_result_score'
        ),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<AssessmentResult {self.assessment_id} - {self.criteria_id}>"

class AssessmentHistory(SharedBase, TimestampedMixin):
    """Model for tracking assessment history."""
    __tablename__ = "skill_assessment_assessment_history"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("skill_assessment_skill_assessments.id"), nullable=False)
    change_type = Column(String(50), nullable=False)
    previous_state = Column(JSON)
    new_state = Column(JSON)
    reason = Column(Text, nullable=False)

    # Relationships
    assessment = relationship("app.models.skill_assessment.assessment.assessment.SkillAssessment", back_populates="history")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "change_type IN ('created', 'updated', 'completed', 'archived')",
            name='valid_change_type'
        ),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<AssessmentHistory {self.assessment_id} - {self.change_type}>"

class SkillProgress(SharedBase, TimestampedMixin):
    """Model for tracking skill progress over time."""
    __tablename__ = "skill_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete='CASCADE'), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete='CASCADE'), nullable=False)
    skill_level = Column(String(50), nullable=False)
    progress_data = Column(JSON, nullable=False)
    last_assessment_date = Column(TIMESTAMP(timezone=True))
    next_assessment_date = Column(TIMESTAMP(timezone=True))
    goals = Column(JSON)

    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="skill_progress")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="skill_progress")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "skill_level IN ('beginner', 'intermediate', 'advanced', 'expert')",
            name='valid_skill_level'
        ),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<SkillProgress {self.student_id} - {self.activity_id}>"

class AssessmentMetrics(SharedBase, TimestampedMixin):
    """Model for storing assessment metrics and analytics."""
    __tablename__ = "skill_assessment_assessment_metrics"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("skill_assessment_skill_assessments.id", ondelete='CASCADE'), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete='CASCADE'), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete='CASCADE'), nullable=False)
    
    # Performance metrics
    recent_average = Column(Float)
    historical_average = Column(Float)
    trend = Column(Float)
    volatility = Column(Float)
    improvement_rate = Column(Float)
    
    # Additional metrics
    performance_level = Column(String(50))
    progress_level = Column(String(50))
    metrics_data = Column(JSON)
    
    # Relationships
    assessment = relationship("app.models.skill_assessment.assessment.assessment.SkillAssessment", back_populates="metrics")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="assessment_metrics")
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="assessment_metrics")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "performance_level IN ('excellent', 'good', 'average', 'needs_improvement', 'poor')",
            name='valid_performance_level'
        ),
        CheckConstraint(
            "progress_level IN ('rapid', 'steady', 'slow', 'no_progress', 'declining')",
            name='valid_progress_level'
        ),
        CheckConstraint(
            'recent_average IS NULL OR (recent_average >= 0.0 AND recent_average <= 100.0)',
            name='valid_recent_average'
        ),
        CheckConstraint(
            'historical_average IS NULL OR (historical_average >= 0.0 AND historical_average <= 100.0)',
            name='valid_historical_average'
        ),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<AssessmentMetrics {self.assessment_id} - {self.student_id}>"

class SkillModels:
    """Service for managing skill assessment models and operations."""
    
    def __init__(self):
        self.logger = logging.getLogger("skill_models")
        self.assessment_history = []
        self.progress_tracking = {}
        self.skill_benchmarks = {}
        
    async def initialize(self):
        """Initialize skill assessment resources."""
        try:
            await self.load_skill_benchmarks()
            self.logger.info("Skill models initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing skill models: {str(e)}")
            raise
            
    async def cleanup(self):
        """Cleanup skill assessment resources."""
        try:
            self.assessment_history.clear()
            self.progress_tracking.clear()
            self.skill_benchmarks.clear()
            self.logger.info("Skill models cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up skill models: {str(e)}")
            raise
            
    async def load_skill_benchmarks(self):
        """Load skill benchmarks for different activities."""
        try:
            self.skill_benchmarks = {
                "throwing": {
                    "velocity": {"excellent": 30.0, "good": 25.0, "average": 20.0},
                    "accuracy": {"excellent": 0.9, "good": 0.8, "average": 0.7},
                    "form_score": {"excellent": 0.9, "good": 0.8, "average": 0.7}
                },
                "jumping": {
                    "height": {"excellent": 0.6, "good": 0.5, "average": 0.4},
                    "power": {"excellent": 2000, "good": 1800, "average": 1600},
                    "form_score": {"excellent": 0.9, "good": 0.8, "average": 0.7}
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading skill benchmarks: {str(e)}")
            raise 