"""
Dashboard Sharing Models

This module defines the database models for dashboard sharing and exports
in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class DashboardShareConfig(BaseModel, StatusMixin, MetadataMixin):
    """Model for dashboard sharing configuration."""
    __tablename__ = "dashboard_share_configs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    share_type = Column(String, nullable=False)  # link, embed, export
    permissions = Column(JSON, default={})
    expires_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_share_configs")

class DashboardExport(BaseModel, StatusMixin, MetadataMixin):
    """Model for dashboard export history."""
    __tablename__ = "dashboard_share_exports"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    format = Column(String, nullable=False)  # json, csv, pdf
    configuration = Column(JSON, nullable=False)
    file_size = Column(Integer, nullable=True)
    download_count = Column(Integer, default=0)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_exports") 