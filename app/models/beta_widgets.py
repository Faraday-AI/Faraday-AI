"""
Beta Widgets Model

This module defines the BetaWidget model for the beta teacher system.
"""

from sqlalchemy import Column, String, JSON, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.core.base import CoreBase


class BetaWidget(CoreBase):
    """Model for beta widgets in the teacher system."""
    __tablename__ = "beta_widgets"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    widget_type = Column(String(100), nullable=False)
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "widget_type": self.widget_type,
            "configuration": self.configuration,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

