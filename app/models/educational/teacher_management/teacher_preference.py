"""
Teacher Preference Model

This model tracks teacher preferences for various aspects of their work.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class TeacherPreference(Base):
    """Model for teacher preferences."""
    __tablename__ = "teacher_preferences"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    preference_type = Column(String(100), nullable=False)  # Class Size, Teaching Style, etc.
    preference_value = Column(String(500), nullable=False)
    priority = Column(Integer, default=1)  # 1-5 scale
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teacher = relationship("Teacher", back_populates="preferences")

    def __repr__(self):
        return f"<TeacherPreference(id={self.id}, teacher_id={self.teacher_id}, type={self.preference_type})>"