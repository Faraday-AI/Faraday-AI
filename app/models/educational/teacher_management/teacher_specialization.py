"""
Teacher Specialization Model

This model tracks teacher specializations and areas of expertise.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class TeacherSpecialization(Base):
    """Model for teacher specializations."""
    __tablename__ = "teacher_specializations"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    specialization_area = Column(String(100), nullable=False)  # Elementary PE, Secondary PE, etc.
    years_experience = Column(Integer, nullable=False)
    certification_level = Column(String(50), nullable=False)  # Basic, Intermediate, Advanced, Expert
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="specializations")

    def __repr__(self):
        return f"<TeacherSpecialization(id={self.id}, teacher_id={self.teacher_id}, area={self.specialization_area})>"