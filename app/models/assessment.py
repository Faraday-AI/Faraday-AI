"""
Assessment Models

This module contains models for activity assessments.
"""

from datetime import datetime
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.physical_education.student.models import Student
from app.models.physical_education.pe_enums.pe_types import (
    AssessmentType,
    AssessmentStatus,
    AssessmentLevel,
    AssessmentTrigger,
    AssessmentResult,
    CriteriaType,
    ChangeType,
    AnalysisType,
    AnalysisStatus,
    AnalysisLevel,
    AnalysisTrigger,
    ConfidenceLevel,
    PerformanceLevel,
    RiskLevel,
    SkillLevel,
    ProgressType,
    ProgressStatus
)

class GeneralAssessment(SharedBase):
    """Model for activity assessments."""
    __tablename__ = "general_assessments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    type = Column(Enum(AssessmentType), nullable=False)
    status = Column(Enum(AssessmentStatus), nullable=False, default=AssessmentStatus.PENDING)
    level = Column(Enum(AssessmentLevel), nullable=False)
    trigger = Column(Enum(AssessmentTrigger), nullable=False)
    result = Column(Enum(AssessmentResult), nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
    criteria = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="general_assessments")
    student = relationship("app.models.physical_education.student.models.Student", back_populates="assessments")
    criteria_results = relationship("app.models.assessment.AssessmentCriteria", back_populates="assessment")
    history = relationship("app.models.assessment.AssessmentHistory", back_populates="assessment")
    skill_assessments = relationship("app.models.assessment.SkillAssessment", back_populates="assessment")

class AssessmentCriteria(SharedBase):
    """Model for assessment criteria results."""
    __tablename__ = "general_assessment_criteria"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("general_assessments.id"), nullable=False)
    type = Column(Enum(CriteriaType), nullable=False)
    score = Column(Float, nullable=False)
    feedback = Column(String, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessment = relationship("app.models.assessment.GeneralAssessment", back_populates="criteria_results")

class AssessmentChange(SharedBase):
    """Model for tracking assessment changes."""
    __tablename__ = "assessment_changes"

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("general_assessments.id"), nullable=False)
    type = Column(Enum(ChangeType), nullable=False)
    previous_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(String, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    meta_data = Column(JSON, nullable=True)

    # Relationships
    assessment = relationship("app.models.assessment.GeneralAssessment")
    user = relationship("app.models.core.user.User")

class AssessmentHistory(SharedBase):
    """Model for tracking assessment history."""
    __tablename__ = "general_assessment_history"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("general_assessments.id"), nullable=False)
    status = Column(Enum(AssessmentStatus), nullable=False)
    score = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
    criteria_results = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessment = relationship("app.models.assessment.GeneralAssessment", back_populates="history")

class SkillAssessment(SharedBase):
    """Model for skill-specific assessments."""
    __tablename__ = "general_skill_assessments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("general_assessments.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    skill_level = Column(Enum(SkillLevel), nullable=False)
    performance_level = Column(Enum(PerformanceLevel), nullable=False)
    confidence_level = Column(Enum(ConfidenceLevel), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    analysis_level = Column(Enum(AnalysisLevel), nullable=False)
    analysis_status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING)
    analysis_trigger = Column(Enum(AnalysisTrigger), nullable=False)
    score = Column(Float, nullable=True)
    feedback = Column(String, nullable=True)
    criteria = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    assessment = relationship("app.models.assessment.GeneralAssessment", back_populates="skill_assessments")

class SkillProgress(SharedBase):
    """Model for tracking skill progress over time."""
    __tablename__ = "general_skill_progress"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    type = Column(Enum(ProgressType), nullable=False)
    status = Column(Enum(ProgressStatus), nullable=False, default=ProgressStatus.NOT_STARTED)
    current_level = Column(Enum(SkillLevel), nullable=False)
    target_level = Column(Enum(SkillLevel), nullable=False)
    confidence_level = Column(Enum(ConfidenceLevel), nullable=False)
    performance_level = Column(Enum(PerformanceLevel), nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    progress_percentage = Column(Float, default=0.0)
    assessment_count = Column(Integer, default=0)
    last_assessment_id = Column(Integer, ForeignKey("general_assessments.id"))
    last_assessment_date = Column(DateTime)
    next_assessment_date = Column(DateTime)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("app.models.physical_education.student.models.Student", back_populates="general_skill_progress")
    last_assessment = relationship("app.models.assessment.GeneralAssessment", foreign_keys=[last_assessment_id])

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

__all__ = [
    'GeneralAssessment',
    'AssessmentCriteria',
    'AssessmentChange',
    'AssessmentHistory',
    'SkillAssessment',
    'SkillProgress',
    'SkillModels'
] 