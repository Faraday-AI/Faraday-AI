"""
Grade Model

This module defines the database model for student grades in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.physical_education.base.base_class import Base

class Grade(Base):
    """Model for tracking student grades."""
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    grade = Column(Float)
    feedback = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime)
    grader_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)  # submitted, graded, returned

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    assignment = relationship("Assignment")
    grader = relationship("User", foreign_keys=[grader_id]) 