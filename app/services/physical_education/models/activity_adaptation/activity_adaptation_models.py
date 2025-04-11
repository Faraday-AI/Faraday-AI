from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class ActivityAdaptation(Base):
    """Model for storing activity adaptations."""
    __tablename__ = "activity_adaptations"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    adaptation_type = Column(String, nullable=False)
    adaptation_details = Column(JSON, nullable=False)
    reason = Column(Text, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity = relationship("Activity", back_populates="adaptations")
    student = relationship("Student", back_populates="activity_adaptations")

class AdaptationHistory(Base):
    """Model for tracking adaptation history."""
    __tablename__ = "adaptation_history"

    id = Column(Integer, primary_key=True, index=True)
    adaptation_id = Column(Integer, ForeignKey("activity_adaptations.id"), nullable=False)
    previous_state = Column(JSON, nullable=False)
    new_state = Column(JSON, nullable=False)
    change_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    adaptation = relationship("ActivityAdaptation", back_populates="history")

# Add relationship to ActivityAdaptation
ActivityAdaptation.history = relationship("AdaptationHistory", back_populates="adaptation") 