"""
Educational Class Model

This model represents educational classes in the system.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class EducationalClass(Base):
    """Model for educational classes."""
    __tablename__ = "educational_classes"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(100), nullable=False)
    class_type = Column(String(50), nullable=False)  # Regular, Honors, AP, Remedial, Enrichment
    subject = Column(String(100), nullable=False)
    grade_level = Column(Integer, nullable=False)
    max_students = Column(Integer, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="educational_classes")
    students = relationship("EducationalClassStudent", back_populates="educational_class")
    attendance_records = relationship("ClassAttendance", back_populates="educational_class")
    plans = relationship("ClassPlan", back_populates="educational_class")
    schedules = relationship("ClassSchedule", back_populates="educational_class")

    def __repr__(self):
        return f"<EducationalClass(id={self.id}, name={self.class_name}, subject={self.subject})>"