"""
Environmental Alert Model

This module defines the database model for environmental alerts in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.environmental.base.base import EnvironmentalBaseModel
from app.models.core.base import StatusMixin

class EnvironmentalAlert(EnvironmentalBaseModel, StatusMixin):
    """
    Represents an alert triggered by environmental conditions.
    """
    __tablename__ = "environmental_alerts"

    id = Column(Integer, primary_key=True, index=True)
    condition_id = Column(Integer, ForeignKey("environmental_conditions.id"), nullable=False)
    alert_type = Column(String, nullable=False)  # e.g., "temperature", "air_quality"
    severity = Column(String, nullable=False)    # e.g., "low", "medium", "high"
    message = Column(String, nullable=False)
    triggered_at = Column(DateTime, nullable=False)
    details = Column(JSON, nullable=True)

    condition = relationship("EnvironmentalCondition")

    def dict(self):
        return {
            "id": self.id,
            "condition_id": self.condition_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "triggered_at": self.triggered_at,
            "details": self.details,
            "status": self.status,
            "meta_data": self.meta_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 