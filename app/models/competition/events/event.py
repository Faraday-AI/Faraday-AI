"""
Competition Event Model

This module defines the CompetitionEvent model for managing individual events within competitions.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin

class CompetitionEvent(BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for individual events within a competition."""
    
    __tablename__ = "competition_events"
    
    id = Column(Integer, primary_key=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    location = Column(String, nullable=False)
    
    # Event details
    description = Column(String, nullable=True)
    rules = Column(JSON, nullable=True)
    scoring_criteria = Column(JSON, nullable=True)
    max_participants = Column(Integer, nullable=True)
    
    # Requirements
    equipment_needed = Column(JSON, nullable=True)
    staff_needed = Column(JSON, nullable=True)
    venue_setup = Column(JSON, nullable=True)
    
    # Results
    results = Column(JSON, nullable=True)
    rankings = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    competition = relationship("Competition", back_populates="events")
    participants = relationship("EventParticipant", back_populates="event")
