"""
Progress metrics model for physical education activities.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase


class ProgressMetrics(SharedBase):
    """Model for tracking detailed progress metrics in physical education activities."""
    
    __tablename__ = "progress_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("progress_tracking.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # e.g., "speed", "accuracy", "endurance"
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)  # e.g., "seconds", "percentage", "reps"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    context_data = Column(JSON, nullable=True)  # Additional context for the metric
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    progress_record = relationship("ProgressModel", back_populates="metrics")
    
    def __repr__(self):
        return f"<ProgressMetrics(progress_id={self.progress_id}, metric_type={self.metric_type}, metric_value={self.metric_value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "progress_id": self.progress_id,
            "metric_type": self.metric_type,
            "metric_value": self.metric_value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 