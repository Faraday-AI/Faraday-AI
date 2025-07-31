"""
Environmental Models

This module defines environmental models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.core.base import CoreBase
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = CoreBase
TimestampMixin = TimestampedMixin

# Import Activity model to ensure it's registered with SQLAlchemy
from app.models.physical_education.activity.models import Activity

class EnvironmentalCondition(BaseModelMixin, TimestampMixin):
    """Model for environmental conditions."""
    
    __tablename__ = "environmental_conditions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    precipitation = Column(String(50))
    air_quality = Column(String(50))
    condition_metadata = Column(JSON)
    
    # Relationships
    activity = relationship("Activity", back_populates="environmental_conditions")
    impacts = relationship("ActivityEnvironmentalImpact", back_populates="condition")
    alerts = relationship("EnvironmentalAlert", back_populates="condition")

class EnvironmentalConditionCreate(BaseModel):
    """Pydantic model for creating environmental conditions."""
    
    activity_id: int
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[str] = None
    air_quality: Optional[str] = None
    condition_metadata: Optional[dict] = None

class EnvironmentalConditionUpdate(BaseModel):
    """Pydantic model for updating environmental conditions."""
    
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[str] = None
    air_quality: Optional[str] = None
    condition_metadata: Optional[dict] = None

class EnvironmentalConditionResponse(BaseModel):
    """Pydantic model for environmental condition responses."""
    
    id: int
    activity_id: int
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[str] = None
    air_quality: Optional[str] = None
    condition_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityEnvironmentalImpact(BaseModelMixin, TimestampMixin):
    """Model for tracking how environmental conditions affect specific activities."""
    __tablename__ = "activity_environmental_impacts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    condition_id = Column(Integer, ForeignKey("environmental_conditions.id"), nullable=False)
    impact_level = Column(String(20), default="LOW")
    description = Column(Text)
    mitigation_strategy = Column(Text)
    impact_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    activity = relationship("Activity", back_populates="environmental_impacts")
    condition = relationship("EnvironmentalCondition", back_populates="impacts")

class EnvironmentalAlert(BaseModelMixin, TimestampMixin):
    """Model for environmental alerts and warnings."""
    __tablename__ = "environmental_alerts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    condition_id = Column(Integer, ForeignKey("environmental_conditions.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="LOW")
    message = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    alert_metadata = Column(JSON)  # Renamed from metadata
    
    # Relationships
    condition = relationship("EnvironmentalCondition", back_populates="alerts") 