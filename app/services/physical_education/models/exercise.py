from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Exercise(Base):
    """Model for exercises within activities."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    duration_minutes = Column(Integer, nullable=False)
    intensity = Column(String, nullable=False)  # low, medium, high
    equipment_needed = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity = relationship("Activity", back_populates="exercises")

    def __repr__(self):
        return f"<Exercise {self.name}>" 