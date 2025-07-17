"""
Environmental Condition Model

This module defines the database model for environmental conditions in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.environmental.base.base import EnvironmentalBaseModel
from app.models.core.base import StatusMixin

class EnvironmentalCondition(EnvironmentalBaseModel, StatusMixin):
    """
    Represents a set of environmental conditions at a specific location and time.
    """
    __tablename__ = "environmental_conditions"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    location = relationship("Location", back_populates="environmental_conditions")
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    air_quality = Column(String, nullable=True)
    noise_level = Column(Float, nullable=True)
    light_level = Column(Float, nullable=True)
    recorded_at = Column(DateTime, nullable=False)

    def dict(self):
        return {
            "id": self.id,
            "location_id": self.location_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "air_quality": self.air_quality,
            "noise_level": self.noise_level,
            "light_level": self.light_level,
            "recorded_at": self.recorded_at,
            "status": self.status,
            "meta_data": self.meta_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 