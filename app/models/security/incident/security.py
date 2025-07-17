"""
Security Incident Models

This module contains models for security incident tracking and management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.models.physical_education.base.base_class import Base

class IncidentSeverity(enum.Enum):
    """Enum for incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(enum.Enum):
    """Enum for incident status."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

class SecurityIncidentManagement(Base):
    """Model for security incident management."""
    
    __tablename__ = "security_incident_management"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(Enum(IncidentSeverity), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    details = Column(JSON, nullable=True)
    resolution = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reported_by], back_populates="security_incidents")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_incidents") 