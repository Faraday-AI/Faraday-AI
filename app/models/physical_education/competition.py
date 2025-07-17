"""
Competition Models

This module defines competition models for physical education.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.base import Base, BaseModel as SQLBaseModel
from app.models.mixins import TimestampedMixin

# Re-export for backward compatibility
BaseModelMixin = SQLBaseModel
TimestampMixin = TimestampedMixin

# Pydantic models for API
class CompetitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    location: str
    status: str = "PLANNED"
    type: str
    rules: dict
    metadata: Optional[dict] = None

class CompetitionCreate(CompetitionBase):
    pass

class CompetitionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    rules: Optional[dict] = None
    metadata: Optional[dict] = None

class CompetitionResponse(CompetitionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CompetitionEventBase(BaseModel):
    competition_id: int
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    event_type: str
    rules: dict
    metadata: Optional[dict] = None

class CompetitionEventCreate(CompetitionEventBase):
    pass

class CompetitionEventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_type: Optional[str] = None
    rules: Optional[dict] = None
    metadata: Optional[dict] = None

class CompetitionEventResponse(CompetitionEventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CompetitionParticipantBase(BaseModel):
    competition_id: int
    student_id: int
    team_name: Optional[str] = None
    registration_date: datetime
    status: str = "REGISTERED"
    metadata: Optional[dict] = None

class CompetitionParticipantCreate(CompetitionParticipantBase):
    pass

class CompetitionParticipantUpdate(BaseModel):
    team_name: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None

class CompetitionParticipantResponse(CompetitionParticipantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EventParticipantBase(BaseModel):
    event_id: int
    participant_id: int
    registration_date: datetime
    status: str = "REGISTERED"
    result: Optional[dict] = None
    metadata: Optional[dict] = None

class EventParticipantCreate(EventParticipantBase):
    pass

class EventParticipantUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[dict] = None
    metadata: Optional[dict] = None

class EventParticipantResponse(EventParticipantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True) 