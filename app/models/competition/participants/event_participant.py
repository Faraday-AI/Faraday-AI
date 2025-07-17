"""
Event Participant Model

This module defines the EventParticipant model for managing participant registrations in specific events.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import BaseModel, TimestampedMixin, StatusMixin, MetadataMixin

class EventParticipant(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for participant registrations in specific events."""
    
    __tablename__ = "competition_event_participants"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("competition_base_events.id"), nullable=False, index=True)
    participant_id = Column(Integer, ForeignKey("competition_base_participants.id"), nullable=False, index=True)
    
    # Registration details
    registration_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    
    # Performance
    score = Column(JSON, nullable=True)
    ranking = Column(Integer, nullable=True)
    disqualification_reason = Column(String, nullable=True)
    
    # Notes
    notes = Column(String, nullable=True)
    
    # Relationships
    event = relationship("CompetitionEvent", back_populates="participants")
    participant = relationship("CompetitionParticipant", back_populates="event_participations")
