"""
Goal Setting Models

This module defines goal setting models for physical education.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship

from app.models.base import Base

class PhysicalEducationGoal(Base):
    """Model for tracking student physical education goals."""
    
    __tablename__ = "physical_education_goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Float)
    current_value = Column(Float)
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime)
    status = Column(String(20), default="ACTIVE")
    notes = Column(Text)
    goal_metadata = Column(JSON)
    
    # Relationships will be set up by setup_physical_education_goal_relationships() after model initialization
    # This avoids circular import issues during SQLAlchemy mapper configuration
    pass  # Relationships can be added via setup function if needed 