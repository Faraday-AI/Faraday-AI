"""
Teacher Schedule Model

This model tracks teacher schedules and time commitments.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class TeacherSchedule(Base):
    """Model for teacher schedules."""
    __tablename__ = "teacher_schedules"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    schedule_type = Column(String(50), nullable=False)  # Regular, Substitute, Special Event, etc.
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1=Monday, 7=Sunday
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="schedules")

    def __repr__(self):
        return f"<TeacherSchedule(id={self.id}, teacher_id={self.teacher_id}, type={self.schedule_type})>"