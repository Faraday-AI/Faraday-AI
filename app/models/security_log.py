"""
Security Log Model

This module defines the SecurityLog model for tracking security-related events.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.shared_base import SharedBase

class SecurityLog(SharedBase):
    """Model for tracking security-related events."""
    __tablename__ = "security_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)  # HIGH, MEDIUM, LOW
    source_ip = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(Text, nullable=False)
    security_metadata = Column(JSON)  # Additional security data
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SecurityLog {self.event_type} - {self.severity}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'user_id': self.user_id,
            'description': self.description,
            'security_metadata': self.security_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 