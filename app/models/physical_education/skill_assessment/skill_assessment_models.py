"""
Skill Assessment Models

This module defines skill assessment models for physical education.
"""

import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

class SkillAssessment(Base):
    """Model for skill assessments."""
    __tablename__ = "pe_skill_assessment_records"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    score = Column(Float, nullable=False)
    level = Column(String(20), nullable=False)
    criteria_data = Column(JSON, name='criteria')  # Explicitly map to 'criteria' column
    assessment_metadata = Column(JSON, nullable=True)
    
    # Relationships - will be set up by setup_skill_assessment_relationships() after model initialization
    # This avoids circular import issues during SQLAlchemy mapper configuration
    pass  # Relationships added via setup_skill_assessment_relationships()

class AssessmentCriteria(BaseModelMixin, TimestampMixin):
    """Model for assessment criteria."""
    __tablename__ = "pe_skill_assessment_criteria"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("pe_skill_assessment_records.id"), nullable=False)
    criterion = Column(Text, nullable=False)
    score = Column(Float)
    notes = Column(Text)
    criteria_metadata = Column(JSONB)  # Renamed from metadata
    
    # Relationships - will be set up by setup_skill_assessment_relationships() after model initialization
    # This avoids circular import issues and ambiguous class name resolution during SQLAlchemy mapper configuration
    pass  # Relationship added via setup_skill_assessment_relationships()

class Skill(Base):
    """Model for skills."""
    __tablename__ = "skills"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)
    skill_metadata = Column(JSON, nullable=True)
    
    # Relationships - will be set up by setup_skill_assessment_relationships() after model initialization
    # This avoids ambiguous class name resolution during SQLAlchemy mapper configuration
    progressions = relationship("SkillProgression", back_populates="skill")
    criteria = relationship("SkillCriteria", back_populates="skill")
    pass  # assessments relationship added via setup_skill_assessment_relationships()

class SkillProgression(BaseModelMixin, TimestampMixin):
    """Model for skill progressions."""
    __tablename__ = "skill_progressions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    level = Column(String(20), nullable=False)
    description = Column(Text)
    requirements = Column(JSONB)
    progression_metadata = Column(JSONB)  # Renamed from metadata
    
    # Relationships
    skill = relationship("Skill", back_populates="progressions")

class SkillCriteria(Base):
    """Model for skill assessment criteria."""
    __tablename__ = "skill_criteria"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    weight = Column(Float, nullable=False)
    criteria_metadata = Column(JSON, nullable=True)

    # Relationships
    skill = relationship("Skill", back_populates="criteria")

class SkillLevel(Base):
    """Model for skill levels."""
    __tablename__ = "skill_levels"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    level = Column(String, nullable=False)
    description = Column(String, nullable=True)
    requirements = Column(JSON, nullable=True)
    level_metadata = Column(JSON, nullable=True)

    # Relationships - will be set up by setup_skill_assessment_relationships() after model initialization
    # This avoids missing back_populates property errors during SQLAlchemy mapper configuration
    pass  # Relationship added via setup_skill_assessment_relationships()

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