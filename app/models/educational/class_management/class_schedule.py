"""
Class Schedule Model

This model represents class schedules and timing.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class ClassSchedule(Base):
    """Model for class schedules."""
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("educational_classes.id"), nullable=False)
    schedule_type = Column(String(50), nullable=False)  # Regular, Special Event, Field Trip, Assembly
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1=Monday, 7=Sunday
    room_number = Column(String(50), nullable=True)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    educational_class = relationship("EducationalClass", back_populates="schedules")

    def __repr__(self):
        return f"<ClassSchedule(id={self.id}, class_id={self.class_id}, type={self.schedule_type})>"