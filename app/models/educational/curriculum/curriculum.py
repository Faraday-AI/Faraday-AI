"""
Curriculum models for managing physical education programs.

This module contains models for defining and managing PE curricula,
including standards, learning objectives, and assessment criteria.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.shared_base import SharedBase as Base
from app.models.core.base import NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin
from app.models.educational.curriculum.lesson_plan import LessonPlan

class CurriculumBaseModel(Base, TimestampedMixin, MetadataMixin):
    """Base model for curriculum with metadata, audit, and validation support."""
    
    __abstract__ = True
    
    # Metadata fields
    version = Column(Integer, nullable=False, default=1)
    version_history = Column(JSON, nullable=True, default=list)
    
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
            "version": self.version,
            "version_history": self.version_history,
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

class Curriculum(CurriculumBaseModel, NamedMixin, StatusMixin):
    """Model for PE curriculum management."""
    
    __tablename__ = "curriculum"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    grade_level = Column(String, nullable=False, index=True)
    academic_year = Column(String, nullable=False, index=True)
    
    # Standards and objectives
    learning_standards = Column(JSON, nullable=False)  # Educational standards
    learning_objectives = Column(JSON, nullable=False)  # Specific objectives
    core_competencies = Column(JSON, nullable=False)  # Required skills
    
    # Content organization
    unit_data = Column(JSON, nullable=False)  # Teaching units
    progression_path = Column(JSON, nullable=False)  # Skill progression
    time_allocation = Column(JSON, nullable=False)  # Time per unit
    
    # Assessment framework
    assessment_criteria = Column(JSON, nullable=False)
    evaluation_methods = Column(JSON, nullable=False)
    grading_rubrics = Column(JSON, nullable=True)
    
    # Resources
    required_equipment = Column(JSON, nullable=True)
    teaching_materials = Column(JSON, nullable=True)
    support_resources = Column(JSON, nullable=True)
    
    # Adaptations
    modifications = Column(JSON, nullable=True)  # For different abilities
    accommodations = Column(JSON, nullable=True)  # Special needs
    differentiation_strategies = Column(JSON, nullable=True)
    
    # Implementation
    teaching_strategies = Column(JSON, nullable=True)
    safety_guidelines = Column(JSON, nullable=True)
    best_practices = Column(JSON, nullable=True)
    
    # Tracking
    implementation_status = Column(JSON, nullable=True)
    effectiveness_metrics = Column(JSON, nullable=True)
    feedback_data = Column(JSON, nullable=True)
    
    # Relationships
    units = relationship("app.models.educational.curriculum.curriculum.CurriculumUnit", back_populates="curriculum", cascade="all, delete-orphan", overlaps="curriculum,units")
    assessments = relationship("Assessment", back_populates="curriculum", overlaps="curriculum,assessments")
    standards = relationship("app.models.educational.curriculum.curriculum.CurriculumStandard", secondary="curriculum_standard_association", overlaps="curriculum,standards")

class CurriculumUnit(CurriculumBaseModel, NamedMixin):
    """Model for curriculum units."""
    
    __tablename__ = "curriculum_units"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    curriculum_id = Column(Integer, ForeignKey("curriculum.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    
    # Unit content
    learning_objectives = Column(JSON, nullable=False)
    key_concepts = Column(JSON, nullable=False)
    skill_focus = Column(JSON, nullable=False)
    
    # Activities
    core_activities = Column(JSON, nullable=False)
    extension_activities = Column(JSON, nullable=True)
    assessment_activities = Column(JSON, nullable=True)
    
    # Resources
    equipment_needed = Column(JSON, nullable=True)
    teaching_resources = Column(JSON, nullable=True)
    support_materials = Column(JSON, nullable=True)
    
    # Implementation
    teaching_points = Column(JSON, nullable=True)
    safety_considerations = Column(JSON, nullable=True)
    differentiation = Column(JSON, nullable=True)
    
    # Progress tracking
    completion_criteria = Column(JSON, nullable=False)
    progress_indicators = Column(JSON, nullable=True)
    assessment_methods = Column(JSON, nullable=True)
    
    # Relationships
    curriculum = relationship("app.models.educational.curriculum.curriculum.Curriculum", back_populates="units", overlaps="curriculum,units")

class CurriculumStandard(CurriculumBaseModel, NamedMixin):
    """Model for curriculum standards."""
    
    __tablename__ = "curriculum_standards"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    grade_level = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    
    # Standard details
    performance_indicators = Column(JSON, nullable=False)
    assessment_criteria = Column(JSON, nullable=False)
    learning_outcomes = Column(JSON, nullable=False)
    
    # Implementation
    teaching_strategies = Column(JSON, nullable=True)
    resources_needed = Column(JSON, nullable=True)
    assessment_methods = Column(JSON, nullable=True)
    
    # Tracking
    mastery_levels = Column(JSON, nullable=True)
    progress_metrics = Column(JSON, nullable=True)
    evaluation_rubrics = Column(JSON, nullable=True)
    
    # Relationships
    curricula = relationship("app.models.educational.curriculum.curriculum.Curriculum", secondary="curriculum_standard_association", overlaps="curriculum,standards")

# Association table for curriculum standards
curriculum_standard_association = Table(
    'curriculum_standard_association',
    Base.metadata,
    Column('curriculum_id', Integer, ForeignKey('curriculum.id'), primary_key=True),
    Column('standard_id', Integer, ForeignKey('curriculum_standards.id'), primary_key=True)
) 