"""
Competition Participant Model

This module defines the CompetitionParticipant model for managing competition participants.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import BaseModel, TimestampedMixin, StatusMixin, MetadataMixin

class CompetitionParticipant(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for competition participants."""
    
    __tablename__ = "competition_participants"
    
    id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    division = Column(String, nullable=True)
    
    # Registration details
    registration_number = Column(String, nullable=True)
    division_assignment = Column(String, nullable=True)
    weight_class = Column(String, nullable=True)
    age_group = Column(String, nullable=True)
    
    # Requirements
    waiver_signed = Column(Boolean, default=False)
    medical_clearance = Column(Boolean, default=False)
    equipment_checked = Column(Boolean, default=False)
    
    # Performance
    results = Column(JSON, nullable=True)
    achievements = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    competition = relationship("Competition", back_populates="participants")
    student = relationship("Student")
    event_participations = relationship("EventParticipant", back_populates="participant")
