"""Activity adaptation models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.models.physical_education.base.base_class import Base
from app.models.physical_education.activity import Activity
from app.models.physical_education.student.student import StudentHealthProfile
from app.models.core.user import User

class AdaptationType(str, Enum):
    EQUIPMENT = "equipment"
    INTENSITY = "intensity"
    DURATION = "duration"
    TECHNIQUE = "technique"
    ASSISTANCE = "assistance"
    MODIFICATION = "modification"
    OTHER = "other"

class ActivityAdaptation(Base):
    """Model for activity adaptations."""
    __tablename__ = "physical_education_activity_adaptations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_health.id"), nullable=False)
    adaptation_type = Column(String(50), nullable=False)
    description = Column(String(1000), nullable=False)
    reason = Column(String(1000))  # Reason for adaptation
    equipment_needed = Column(JSON)  # Modified equipment requirements
    instructions = Column(String(1000))  # Modified instructions
    safety_considerations = Column(String(1000))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="pe_adaptations")
    student = relationship("app.models.physical_education.student.student.StudentHealthProfile", back_populates="activity_adaptations")
    creator = relationship("app.models.core.user.User", back_populates="created_adaptations")
    history = relationship("app.models.activity_adaptation.activity.activity_adaptation.AdaptationHistory", back_populates="adaptation")

class AdaptationHistory(Base):
    """Model for tracking adaptation history."""
    __tablename__ = "pe_activity_adaptation_history"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    adaptation_id = Column(Integer, ForeignKey("physical_education_activity_adaptations.id"), nullable=False)
    date_used = Column(DateTime, nullable=False)
    effectiveness = Column(Integer)  # Scale 1-5
    student_feedback = Column(String(1000))
    instructor_feedback = Column(String(1000))
    issues_encountered = Column(JSON)
    modifications_made = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    adaptation = relationship("app.models.activity_adaptation.activity.activity_adaptation.ActivityAdaptation", back_populates="history") 