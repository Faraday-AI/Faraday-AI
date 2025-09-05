"""
Teacher Availability Model

This model tracks teacher availability for scheduling and planning purposes.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class TeacherAvailability(Base):
    """Model for teacher availability records."""
    __tablename__ = "teacher_availability"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    availability_type = Column(String(50), nullable=False)  # Available, Busy, Out of Office, On Leave
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="availability_records")

    def __repr__(self):
        return f"<TeacherAvailability(id={self.id}, teacher_id={self.teacher_id}, type={self.availability_type})>"