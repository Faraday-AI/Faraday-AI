"""
Performance Log Model

This module defines the PerformanceLog model for tracking system performance metrics.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.orm import relationship

from app.models.shared_base import SharedBase

class PerformanceLog(SharedBase):
    """Model for tracking system performance metrics."""
    __tablename__ = "performance_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    component = Column(String(100), nullable=False)
    operation = Column(String(100), nullable=False)
    duration = Column(Float, nullable=False)  # Duration in seconds
    status = Column(String(20), nullable=False)  # SUCCESS, ERROR, WARNING
    error_message = Column(Text)
    performance_metadata = Column(JSON)  # Additional performance data
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PerformanceLog {self.component} - {self.operation}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            'id': self.id,
            'component': self.component,
            'operation': self.operation,
            'duration': self.duration,
            'status': self.status,
            'error_message': self.error_message,
            'performance_metadata': self.performance_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 