"""Shared Core Activity model."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float, Text, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.core.base import BaseModel
from app.models.physical_education.pe_enums.pe_types import (
    ActivityType,
    ActivityCategoryType,
    ActivityDifficulty,
    ActivityStatus,
    ActivityFormat,
    ActivityGoal,
    ProgressionLevel,
    PerformanceLevel,
    EquipmentRequirement
)

class CoreActivity(BaseModel):
    """Model for core physical education activities."""
    __tablename__ = 'core_activities'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(Enum(ActivityType), nullable=False)
    difficulty_level = Column(Enum(ActivityDifficulty), nullable=False)
    duration = Column(Integer)  # in minutes
    equipment_needed = Column(Text)
    safety_notes = Column(Text)
    instructions = Column(JSON)
    adaptations = Column(JSON)
    activity_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CoreActivity {self.name} - {self.difficulty_level}>" 