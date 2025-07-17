"""Instructor model for physical education."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum

from app.models.core.base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin

class InstructorStatus(str, Enum):
    """Instructor status options."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"

class Instructor(BaseModel, NamedMixin, TimestampedMixin, StatusMixin):
    """Model for instructors."""
    __tablename__ = "instructors"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    specialization = Column(String)
    certifications = Column(JSON)  # List of certifications
    bio = Column(String)
    hire_date = Column(DateTime, nullable=False)
    termination_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    status = Column(SQLEnum(InstructorStatus, name='instructor_status'), nullable=False, default=InstructorStatus.ACTIVE)

    # Relationships
    # classes = relationship("EducationalClass", back_populates="instructor", overlaps="instructor,classes")

    def __repr__(self):
        return f"<Instructor {self.name}>" 