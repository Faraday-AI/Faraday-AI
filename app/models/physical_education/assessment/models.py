"""
Assessment Models

This module defines assessment-related models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

from app.models.physical_education.pe_enums.pe_types import (
    AssessmentType,
    AssessmentStatus,
    AssessmentLevel,
    AssessmentTrigger,
    CriteriaType,
    ChangeType,
    PerformanceLevel,
    AssessmentResult
)
from app.models.physical_education.relationships import setup_assessment_relationships

class Assessment(BaseModelMixin, TimestampMixin):
    """Base class for assessment models."""
    __tablename__ = 'assessment_base'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    score = Column(Float)
    feedback = Column(Text)
    type = Column(String(50))  # Polymorphic discriminator
    
    __mapper_args__ = {
        'polymorphic_identity': 'assessment_base',
        'polymorphic_on': 'type'
    }

# Initialize relationships - temporarily commented out to fix mapper issues
# setup_assessment_relationships(Assessment)

# Pydantic models for API
class AssessmentCreate(BaseModel):
    """Pydantic model for creating assessments."""
    
    student_id: int
    assessment_type: str
    assessment_date: datetime
    score: Optional[float] = None
    max_score: Optional[float] = None
    notes: Optional[str] = None
    assessment_metadata: Optional[dict] = None

class AssessmentUpdate(BaseModel):
    """Pydantic model for updating assessments."""
    
    assessment_type: Optional[str] = None
    assessment_date: Optional[datetime] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    notes: Optional[str] = None
    assessment_metadata: Optional[dict] = None

class AssessmentResponse(BaseModel):
    """Pydantic model for assessment responses."""
    
    id: int
    student_id: int
    assessment_type: str
    assessment_date: datetime
    score: Optional[float] = None
    max_score: Optional[float] = None
    notes: Optional[str] = None
    assessment_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SkillAssessment(Assessment):
    """Model for skill assessments."""
    __tablename__ = 'skill_assessments'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey('assessment_base.id'), primary_key=True)
    skill_type = Column(String(50), nullable=False)
    skill_level = Column(Enum(PerformanceLevel, name='skill_level_enum'))
    skill_notes = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'skill_assessment',
        'inherit_condition': Assessment.id == id
    }
    
    def __repr__(self):
        return f"<SkillAssessment {self.skill_type} - {self.skill_level}>"

class SkillAssessmentCreate(BaseModel):
    """Pydantic model for creating skill assessments."""
    
    name: str
    description: Optional[str] = None
    type: AssessmentType
    max_score: float
    passing_score: float
    teacher_id: int
    curriculum_id: Optional[int] = None
    skill_name: str
    skill_level: PerformanceLevel
    criteria: str
    demonstration_required: bool = True

class SkillAssessmentUpdate(BaseModel):
    """Pydantic model for updating skill assessments."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AssessmentType] = None
    max_score: Optional[float] = None
    passing_score: Optional[float] = None
    teacher_id: Optional[int] = None
    curriculum_id: Optional[int] = None
    skill_name: Optional[str] = None
    skill_level: Optional[PerformanceLevel] = None
    criteria: Optional[str] = None
    demonstration_required: Optional[bool] = None

class SkillAssessmentResponse(BaseModel):
    """Pydantic model for skill assessment responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    type: AssessmentType
    max_score: float
    passing_score: float
    teacher_id: int
    curriculum_id: Optional[int] = None
    skill_name: str
    skill_level: PerformanceLevel
    criteria: str
    demonstration_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FitnessAssessment(Assessment):
    """Model for fitness assessments."""
    __tablename__ = 'fitness_assessments'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey('assessment_base.id'), primary_key=True)
    fitness_type = Column(String(50), nullable=False)
    fitness_level = Column(String(20))
    fitness_notes = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'fitness_assessment',
        'inherit_condition': Assessment.id == id
    }
    
    def __repr__(self):
        return f"<FitnessAssessment {self.fitness_type} - {self.fitness_level}>"

class FitnessAssessmentCreate(BaseModel):
    """Pydantic model for creating fitness assessments."""
    
    name: str
    description: Optional[str] = None
    type: AssessmentType
    max_score: float
    passing_score: float
    teacher_id: int
    curriculum_id: Optional[int] = None
    fitness_category: str
    target_metrics: str
    measurement_unit: str
    baseline_score: Optional[float] = None
    improvement_target: Optional[float] = None

class FitnessAssessmentUpdate(BaseModel):
    """Pydantic model for updating fitness assessments."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AssessmentType] = None
    max_score: Optional[float] = None
    passing_score: Optional[float] = None
    teacher_id: Optional[int] = None
    curriculum_id: Optional[int] = None
    fitness_category: Optional[str] = None
    target_metrics: Optional[str] = None
    measurement_unit: Optional[str] = None
    baseline_score: Optional[float] = None
    improvement_target: Optional[float] = None

class FitnessAssessmentResponse(BaseModel):
    """Pydantic model for fitness assessment responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    type: AssessmentType
    max_score: float
    passing_score: float
    teacher_id: int
    curriculum_id: Optional[int] = None
    fitness_category: str
    target_metrics: str
    measurement_unit: str
    baseline_score: Optional[float] = None
    improvement_target: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MovementAssessment(Assessment):
    """Model for movement assessments."""
    __tablename__ = 'movement_assessments'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, ForeignKey('assessment_base.id'), primary_key=True)
    movement_type = Column(String(50), nullable=False)
    movement_level = Column(String(20))
    movement_notes = Column(Text)
    
    __mapper_args__ = {
        'polymorphic_identity': 'movement_assessment',
        'inherit_condition': Assessment.id == id
    }
    
    def __repr__(self):
        return f"<MovementAssessment {self.movement_type} - {self.movement_level}>"

class MovementAssessmentCreate(BaseModel):
    """Pydantic model for creating movement assessments."""
    
    name: str
    description: Optional[str] = None
    type: AssessmentType
    max_score: float
    passing_score: float
    teacher_id: int
    curriculum_id: Optional[int] = None
    movement_pattern: str
    technique_criteria: str
    safety_considerations: Optional[str] = None
    modifications: Optional[str] = None

class MovementAssessmentUpdate(BaseModel):
    """Pydantic model for updating movement assessments."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[AssessmentType] = None
    max_score: Optional[float] = None
    passing_score: Optional[float] = None
    teacher_id: Optional[int] = None
    curriculum_id: Optional[int] = None
    movement_pattern: Optional[str] = None
    technique_criteria: Optional[str] = None
    safety_considerations: Optional[str] = None
    modifications: Optional[str] = None

class MovementAssessmentResponse(BaseModel):
    """Pydantic model for movement assessment responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    type: AssessmentType
    max_score: float
    passing_score: float
    teacher_id: int
    curriculum_id: Optional[int] = None
    movement_pattern: str
    technique_criteria: str
    safety_considerations: Optional[str] = None
    modifications: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 