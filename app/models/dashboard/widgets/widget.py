"""
Dashboard Widget Models

This module defines the database models for dashboard widgets
in the Faraday AI system.
"""

from sqlalchemy import Column, String, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class CoreDashboardWidget(BaseModel, StatusMixin, MetadataMixin):
    """Model for core dashboard widget configuration."""
    __tablename__ = "core_dashboard_widgets"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    widget_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    position = Column(JSON, nullable=True)  # x, y coordinates
    size = Column(JSON, nullable=True)  # width, height

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="core_widgets") 