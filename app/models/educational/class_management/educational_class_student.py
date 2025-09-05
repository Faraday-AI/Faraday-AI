"""
Educational Class Student Model

This model represents the relationship between educational classes and students.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class EducationalClassStudent(Base):
    """Model for educational class student enrollments."""
    __tablename__ = "educational_class_students"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("educational_classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    enrollment_date = Column(DateTime, nullable=False)
    enrollment_status = Column(String(50), nullable=False)  # Active, Dropped, Completed, On Hold
    grade = Column(String(10), nullable=True)  # A, B, C, D, F
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    educational_class = relationship("EducationalClass", back_populates="students")
    student = relationship("Student", back_populates="class_enrollments")

    def __repr__(self):
        return f"<EducationalClassStudent(id={self.id}, class_id={self.class_id}, student_id={self.student_id})>"