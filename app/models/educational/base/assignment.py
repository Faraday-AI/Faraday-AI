"""
Assignment Model

This module defines the database model for educational assignments in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.physical_education.base.base_class import Base

class Assignment(Base):
    """Model for managing educational assignments."""
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    rubric_id = Column(Integer, ForeignKey("rubrics.id"))
    status = Column(String)  # draft, published, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User")
    course = relationship("Course")
    rubric = relationship("Rubric", overlaps="rubric")
    grades = relationship("Grade", overlaps="assignment") 