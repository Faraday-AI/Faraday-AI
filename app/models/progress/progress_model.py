"""
Progress tracking model for physical education activities.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase


class ProgressModel(SharedBase):
    """Model for tracking student progress in physical education activities."""
    
    __tablename__ = "progress_tracking"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    completion_time = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    effort_level = Column(Float, nullable=True)
    form_score = Column(Float, nullable=True)
    additional_metrics = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="progress_records")
    activity = relationship("Activity", back_populates="progress_records")
    metrics = relationship("ProgressMetrics", back_populates="progress_record")
    
    def __repr__(self):
        return f"<ProgressModel(student_id={self.student_id}, activity_id={self.activity_id}, timestamp={self.timestamp})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "activity_id": self.activity_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "completion_time": self.completion_time,
            "accuracy": self.accuracy,
            "effort_level": self.effort_level,
            "form_score": self.form_score,
            "additional_metrics": self.additional_metrics,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 