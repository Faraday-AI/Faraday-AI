from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class ActivityPlan(Base):
    """Model for activity plans."""
    __tablename__ = "activity_plans"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    focus_areas = Column(JSON, nullable=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="activity_plans")
    class_ = relationship("Class", back_populates="activity_plans")
    activities = relationship("ActivityPlanActivity", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ActivityPlan {self.id}>" 