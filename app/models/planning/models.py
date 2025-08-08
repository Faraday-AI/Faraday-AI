"""
Planning Models

This module defines planning models for physical education activities.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin
from app.models.physical_education.pe_enums.pe_types import (
    PlanningType,
    PlanningLevel,
    PlanningStatus,
    PlanningTrigger
)

class ActivityPlan(SharedBase, TimestampedMixin):
    """Model for activity planning."""
    
    __tablename__ = "activity_plans_planning"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(100), nullable=False)
    plan_description = Column(Text)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    planning_type = Column(Enum(PlanningType, name='planning_type_enum'), nullable=False)
    planning_level = Column(Enum(PlanningLevel, name='planning_level_enum'), nullable=False)
    planning_status = Column(Enum(PlanningStatus, name='planning_status_enum'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    planning_notes = Column(Text)
    planning_metadata = Column(JSON)
    
    # Relationships
    student = relationship("Student", back_populates="activity_plans")
    metrics = relationship("PlanningMetrics", back_populates="plan")
    history = relationship("PlanningHistory", back_populates="plan")

class PlanningMetrics(SharedBase, TimestampedMixin):
    """Model for planning metrics."""
    
    __tablename__ = "planning_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("activity_plans_planning.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(Float)
    metric_unit = Column(String(20))
    metric_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    metric_notes = Column(Text)
    metric_metadata = Column(JSON)
    
    # Relationships
    plan = relationship("app.models.planning.models.ActivityPlan", back_populates="metrics")

class PlanningHistory(SharedBase, TimestampedMixin):
    """Model for planning history."""
    
    __tablename__ = "planning_history"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("activity_plans_planning.id"), nullable=False)
    history_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    history_type = Column(String(50), nullable=False)
    history_description = Column(Text)
    history_trigger = Column(Enum(PlanningTrigger, name='history_trigger_enum'))
    history_metadata = Column(JSON)
    
    # Relationships
    plan = relationship("app.models.planning.models.ActivityPlan", back_populates="history")

# Pydantic models for API
class ActivityPlanCreate(BaseModel):
    """Pydantic model for creating activity plans."""
    
    plan_name: str
    plan_description: Optional[str] = None
    student_id: int
    planning_type: PlanningType
    planning_level: PlanningLevel
    planning_status: PlanningStatus
    start_date: datetime
    end_date: datetime
    planning_notes: Optional[str] = None
    planning_metadata: Optional[dict] = None

class ActivityPlanUpdate(BaseModel):
    """Pydantic model for updating activity plans."""
    
    plan_name: Optional[str] = None
    plan_description: Optional[str] = None
    planning_type: Optional[PlanningType] = None
    planning_level: Optional[PlanningLevel] = None
    planning_status: Optional[PlanningStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    planning_notes: Optional[str] = None
    planning_metadata: Optional[dict] = None

class ActivityPlanResponse(BaseModel):
    """Pydantic model for activity plan responses."""
    
    id: int
    plan_name: str
    plan_description: Optional[str] = None
    student_id: int
    planning_type: PlanningType
    planning_level: PlanningLevel
    planning_status: PlanningStatus
    start_date: datetime
    end_date: datetime
    planning_notes: Optional[str] = None
    planning_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 