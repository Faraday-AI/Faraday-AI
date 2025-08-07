"""
Progress goal model for physical education activities.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase


class ProgressGoal(SharedBase):
    """Model for tracking progress goals in physical education activities."""
    
    __tablename__ = "progress_goals"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    goal_type = Column(String(50), nullable=False)  # e.g., "accuracy", "speed", "endurance"
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_achieved = Column(Boolean, default=False)
    progress_percentage = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="progress_goals")
    activity = relationship("Activity", back_populates="progress_goals")
    
    def __repr__(self):
        return f"<ProgressGoal(student_id={self.student_id}, goal_type={self.goal_type}, target_value={self.target_value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "activity_id": self.activity_id,
            "goal_type": self.goal_type,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "is_achieved": self.is_achieved,
            "progress_percentage": self.progress_percentage,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 