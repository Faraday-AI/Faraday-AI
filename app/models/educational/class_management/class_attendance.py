"""
Class Attendance Model

This model tracks student attendance in educational classes.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class ClassAttendance(Base):
    """Model for class attendance records."""
    __tablename__ = "class_attendance"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("educational_classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    attendance_date = Column(DateTime, nullable=False)
    attendance_status = Column(String(50), nullable=False)  # Present, Absent, Late, Excused, Tardy
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    educational_class = relationship("EducationalClass", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")

    def __repr__(self):
        return f"<ClassAttendance(id={self.id}, class_id={self.class_id}, student_id={self.student_id})>"