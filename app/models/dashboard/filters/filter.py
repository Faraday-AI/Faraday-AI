"""
Dashboard Filter Models

This module defines the database models for dashboard filters and search
in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class DashboardFilterConfig(BaseModel, StatusMixin, MetadataMixin):
    """Model for dashboard filter configuration."""
    __tablename__ = "dashboard_filter_configs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    filter_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    applied_to = Column(JSON, default=[])  # list of widget IDs

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_filter_configs")

class DashboardSearch(BaseModel, StatusMixin, MetadataMixin):
    """Model for dashboard search history."""
    __tablename__ = "dashboard_filter_searches"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    query = Column(String, nullable=False)
    filters = Column(JSON, default={})
    results_count = Column(Integer, nullable=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_searches") 