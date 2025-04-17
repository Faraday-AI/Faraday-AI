from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class RoutineStatus(str, enum.Enum):
    """Enum for routine status."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Routine(Base):
    """Model for physical education routines."""
    __tablename__ = 'routines'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    class_id = Column(Integer, ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    focus_areas = Column(String)  # Stored as JSON string
    status = Column(Enum(RoutineStatus), default=RoutineStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_ = relationship("Class", back_populates="routines")
    activities = relationship("RoutineActivity", back_populates="routine", cascade="all, delete-orphan")
    performances = relationship("RoutinePerformance", back_populates="routine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Routine {self.name}>" 