"""
Injury Prevention Models

This module defines injury prevention models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

class InjuryRiskFactor(BaseModelMixin, TimestampMixin):
    """Model for injury risk factors."""
    
    __tablename__ = "injury_risk_factors"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    risk_level = Column(String(20))
    factor_metadata = Column(JSON)
    
    # Relationships
    activities = relationship("ActivityInjuryPrevention", back_populates="risk_factor")

class PreventionMeasure(BaseModelMixin, TimestampMixin):
    """Model for prevention measures."""
    
    __tablename__ = "prevention_measures"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    effectiveness = Column(String(20))
    measure_metadata = Column(JSON)
    
    # Relationships
    activities = relationship("ActivityInjuryPrevention", back_populates="prevention_measure")

class PreventionAssessment(BaseModelMixin, TimestampMixin):
    """Model for prevention assessments."""
    
    __tablename__ = "prevention_assessments"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    risk_factor_id = Column(Integer, ForeignKey("injury_risk_factors.id"), nullable=False)
    measure_id = Column(Integer, ForeignKey("prevention_measures.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    effectiveness = Column(String(20))
    assessment_notes = Column(Text)
    assessment_metadata = Column(JSON)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="prevention_assessments")
    risk_factor = relationship("InjuryRiskFactor", back_populates="assessments")
    prevention_measure = relationship("PreventionMeasure", back_populates="assessments")

class InjuryPrevention(BaseModelMixin, TimestampMixin):
    """Model for injury prevention measures."""
    
    __tablename__ = "injury_preventions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    risk_level = Column(String(20))
    prevention_metadata = Column(JSON)
    
    # Relationships
    activities = relationship("ActivityInjuryPrevention", back_populates="prevention")

class ActivityInjuryPrevention(BaseModelMixin, TimestampMixin):
    """Model for linking activities to injury prevention measures."""
    
    __tablename__ = "activity_injury_preventions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    prevention_id = Column(Integer, ForeignKey("injury_preventions.id"), nullable=False)
    priority = Column(Integer)
    prevention_metadata = Column(JSON)
    
    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="injury_preventions")
    prevention = relationship("InjuryPrevention", back_populates="activities")

# Pydantic models for API
class InjuryRiskFactorCreate(BaseModel):
    """Pydantic model for creating injury risk factors."""
    
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    factor_metadata: Optional[dict] = None

class InjuryRiskFactorUpdate(BaseModel):
    """Pydantic model for updating injury risk factors."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[str] = None
    factor_metadata: Optional[dict] = None

class InjuryRiskFactorResponse(BaseModel):
    """Pydantic model for injury risk factor responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    factor_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PreventionMeasureCreate(BaseModel):
    """Pydantic model for creating prevention measures."""
    
    name: str
    description: Optional[str] = None
    effectiveness: Optional[str] = None
    measure_metadata: Optional[dict] = None

class PreventionMeasureUpdate(BaseModel):
    """Pydantic model for updating prevention measures."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    effectiveness: Optional[str] = None
    measure_metadata: Optional[dict] = None

class PreventionMeasureResponse(BaseModel):
    """Pydantic model for prevention measure responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    effectiveness: Optional[str] = None
    measure_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PreventionAssessmentCreate(BaseModel):
    """Pydantic model for creating prevention assessments."""
    
    activity_id: int
    risk_factor_id: int
    measure_id: int
    assessment_date: datetime
    effectiveness: Optional[str] = None
    assessment_notes: Optional[str] = None
    assessment_metadata: Optional[dict] = None

class PreventionAssessmentUpdate(BaseModel):
    """Pydantic model for updating prevention assessments."""
    
    activity_id: Optional[int] = None
    risk_factor_id: Optional[int] = None
    measure_id: Optional[int] = None
    assessment_date: Optional[datetime] = None
    effectiveness: Optional[str] = None
    assessment_notes: Optional[str] = None
    assessment_metadata: Optional[dict] = None

class PreventionAssessmentResponse(BaseModel):
    """Pydantic model for prevention assessment responses."""
    
    id: int
    activity_id: int
    risk_factor_id: int
    measure_id: int
    assessment_date: datetime
    effectiveness: Optional[str] = None
    assessment_notes: Optional[str] = None
    assessment_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InjuryPreventionCreate(BaseModel):
    """Pydantic model for creating injury prevention measures."""
    
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    prevention_metadata: Optional[dict] = None

class InjuryPreventionUpdate(BaseModel):
    """Pydantic model for updating injury prevention measures."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[str] = None
    prevention_metadata: Optional[dict] = None

class InjuryPreventionResponse(BaseModel):
    """Pydantic model for injury prevention responses."""
    
    id: int
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    prevention_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 