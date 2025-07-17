"""
Rubric Model

This module defines the database model for assignment rubrics in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.physical_education.base.base_class import Base

class Rubric(Base):
    """Model for managing assignment rubrics."""
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    criteria = Column(JSON)
    total_points = Column(Float)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User")
    assignments = relationship("Assignment", overlaps="rubric") 