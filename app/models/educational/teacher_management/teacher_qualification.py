"""
Teacher Qualification Model

This model tracks teacher educational qualifications and degrees.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class TeacherQualification(Base):
    """Model for teacher qualifications."""
    __tablename__ = "teacher_qualifications"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    degree_type = Column(String(50), nullable=False)  # Bachelor, Master, PhD, etc.
    subject = Column(String(100), nullable=False)  # Physical Education, Health Education, etc.
    institution = Column(String(200), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    gpa = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="qualifications")

    def __repr__(self):
        return f"<TeacherQualification(id={self.id}, teacher_id={self.teacher_id}, degree={self.degree_type})>"