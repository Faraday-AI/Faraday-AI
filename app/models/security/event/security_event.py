"""
Security Event Model

This module defines the SecurityEvent model for logging security-related events.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin


class SecurityEvent(SharedBase, TimestampedMixin):
    """Model for logging security-related events."""
    
    __tablename__ = "security_events"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    details = Column(JSONB, nullable=True)  # Additional event details (JSONB for PostgreSQL)
    description = Column(Text, nullable=True)  # Human-readable description
    severity = Column(String(20), nullable=True, default="info")  # info, warning, error, critical
    resource_type = Column(String(50), nullable=True)  # Type of resource accessed
    resource_id = Column(String(100), nullable=True)  # ID of resource accessed
    action = Column(String(50), nullable=True)  # Action performed
    success = Column(String(10), nullable=True, default="unknown")  # success, failure, unknown
    
    # Relationships
    user = relationship("User", back_populates="security_events", lazy="select")
    
    def __repr__(self):
        return f"<SecurityEvent {self.event_type} - User {self.user_id} - {self.created_at}>"

