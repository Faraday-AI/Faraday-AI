"""
Competition and event models for physical education.

This module contains models for managing sports competitions, events,
and related activities in physical education.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin
from app.models.student import Student

class Competition(BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for sports competitions and events."""
    
    __tablename__ = "competitions"
    
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    competition_type = Column(String, nullable=False)  # e.g., tournament, meet, league
    sport_type = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=True)
    location = Column(String, nullable=False)
    
    # Organization details
    organizer = Column(String, nullable=False)
    contact_info = Column(JSON, nullable=True)
    registration_deadline = Column(DateTime, nullable=True)
    max_participants = Column(Integer, nullable=True)
    
    # Competition structure
    divisions = Column(JSON, nullable=True)  # Age/skill divisions
    events = Column(JSON, nullable=True)  # Individual events
    schedule = Column(JSON, nullable=True)  # Event schedule
    rules = Column(JSON, nullable=True)  # Competition rules
    
    # Requirements
    eligibility_criteria = Column(JSON, nullable=True)
    required_documents = Column(JSON, nullable=True)
    equipment_requirements = Column(JSON, nullable=True)
    
    # Resources
    venue_details = Column(JSON, nullable=True)
    staff_assignments = Column(JSON, nullable=True)
    equipment_inventory = Column(JSON, nullable=True)
    
    # Safety and compliance
    safety_protocols = Column(JSON, nullable=True)
    medical_requirements = Column(JSON, nullable=True)
    emergency_procedures = Column(JSON, nullable=True)
    
    # Results and records
    results = Column(JSON, nullable=True)
    rankings = Column(JSON, nullable=True)
    records = Column(JSON, nullable=True)
    
    # Relationships
    participants = relationship("CompetitionParticipant", back_populates="competition")
    events = relationship("CompetitionEvent", back_populates="competition")

class CompetitionEvent(BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for individual events within a competition."""
    
    __tablename__ = "competition_base_events"
    
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

class CompetitionParticipant(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for competition participants."""
    
    __tablename__ = "competition_base_participants"
    
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

class EventParticipant(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for event-specific participation."""
    
    __tablename__ = "competition_base_event_participants"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("competition_base_events.id"), nullable=False, index=True)
    participant_id = Column(Integer, ForeignKey("competition_base_participants.id"), nullable=False, index=True)
    
    # Performance
    start_number = Column(String, nullable=True)
    performance_data = Column(JSON, nullable=True)
    score = Column(Float, nullable=True)
    ranking = Column(Integer, nullable=True)
    
    # Tracking
    check_in_time = Column(DateTime, nullable=True)
    completion_time = Column(DateTime, nullable=True)
    disqualification_reason = Column(String, nullable=True)
    
    # Results
    results = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    event = relationship("CompetitionEvent", back_populates="participants")
    participant = relationship("CompetitionParticipant", back_populates="event_participations") 