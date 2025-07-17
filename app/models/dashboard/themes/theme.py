"""
Dashboard Theme Models

This module defines the database models for dashboard themes
in the Faraday AI system.
"""

from sqlalchemy import Column, String, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class DashboardTheme(BaseModel, StatusMixin, MetadataMixin):
    """Model for dashboard theme configuration."""
    __tablename__ = "dashboard_theme_configs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    colors = Column(JSON, nullable=False)  # color scheme
    typography = Column(JSON, nullable=False)  # font settings
    spacing = Column(JSON, nullable=False)  # layout spacing

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="themes") 