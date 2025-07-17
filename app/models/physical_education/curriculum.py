"""
Curriculum Models

This module defines curriculum models for physical education.
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

class Curriculum(BaseModelMixin, TimestampMixin):
    """Model for physical education curriculum."""
    __tablename__ = "curriculum"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    grade_level = Column(String, nullable=False)
    academic_year = Column(String(20), nullable=False)
    curriculum_metadata = Column(JSON, nullable=True)
    
    # Relationships
    units = relationship("CurriculumUnit", back_populates="curriculum")
    objectives = relationship("CurriculumObjective", back_populates="curriculum")

    def __repr__(self):
        return f"<Curriculum {self.name} - {self.grade_level}>"

class CurriculumUnit(BaseModelMixin, TimestampMixin):
    """Model for curriculum units."""
    __tablename__ = "curriculum_units"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    curriculum_id = Column(Integer, ForeignKey("curriculum.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)  # in weeks
    unit_metadata = Column(JSON, nullable=True)
    
    # Relationships
    curriculum = relationship("Curriculum", back_populates="units")
    lessons = relationship("CurriculumLesson", back_populates="unit")

    def __repr__(self):
        return f"<CurriculumUnit {self.name} - Unit {self.sequence}>"

class CurriculumLesson(BaseModelMixin, TimestampMixin):
    """Model for curriculum lessons."""
    __tablename__ = "curriculum_lessons"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey("curriculum_units.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    lesson_metadata = Column(JSON, nullable=True)
    
    # Relationships
    unit = relationship("CurriculumUnit", back_populates="lessons")
    activities = relationship("CurriculumActivity", back_populates="lesson")

class CurriculumStandard(BaseModelMixin, TimestampMixin):
    """Model for curriculum standards."""
    __tablename__ = 'curriculum_standards'

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('curriculum_units.id'), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    level = Column(String(20), nullable=False)  # BEGINNER, INTERMEDIATE, ADVANCED
    assessment_criteria = Column(JSON, nullable=False)
    extra_data = Column(JSON, nullable=True)

    # Relationships
    unit = relationship("CurriculumUnit", back_populates="standards")

    def __repr__(self):
        return f"<CurriculumStandard {self.code} - {self.category}>"

# Pydantic models for API
class CurriculumBase(BaseModel):
    name: str
    description: Optional[str] = None
    grade_level: str
    academic_year: str
    status: str = "DRAFT"
    metadata: Optional[dict] = None

class CurriculumCreate(CurriculumBase):
    pass

class CurriculumUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    grade_level: Optional[str] = None
    academic_year: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None

class CurriculumResponse(CurriculumBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CurriculumUnitBase(BaseModel):
    curriculum_id: int
    name: str
    description: Optional[str] = None
    sequence: int
    duration_weeks: int
    objectives: dict
    prerequisites: Optional[dict] = None
    metadata: Optional[dict] = None

class CurriculumUnitCreate(CurriculumUnitBase):
    pass

class CurriculumUnitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sequence: Optional[int] = None
    duration_weeks: Optional[int] = None
    objectives: Optional[dict] = None
    prerequisites: Optional[dict] = None
    metadata: Optional[dict] = None

class CurriculumUnitResponse(CurriculumUnitBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CurriculumStandardBase(BaseModel):
    unit_id: int
    code: str
    description: str
    category: str
    level: str
    assessment_criteria: dict
    metadata: Optional[dict] = None

class CurriculumStandardCreate(CurriculumStandardBase):
    pass

class CurriculumStandardUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    assessment_criteria: Optional[dict] = None
    metadata: Optional[dict] = None

class CurriculumStandardResponse(CurriculumStandardBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 