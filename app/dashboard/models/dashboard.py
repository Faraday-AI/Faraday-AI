"""
Database models for dashboard management.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from app.models.shared_base import SharedBase as Base
from .dashboard_models import (
    DashboardWidget,
    Dashboard,
    DashboardShare,
    DashboardFilter,
    DashboardAnalytics
)

# Add relationships to User model
from .user_models import User
User.dashboard_shares = relationship("DashboardShare", back_populates="user")
User.dashboard_filters = relationship("DashboardFilter", back_populates="user")
User.dashboard_analytics = relationship("DashboardAnalytics", back_populates="user")

class DashboardTheme(Base):
    """Dashboard theme configuration."""
    __tablename__ = "dashboard_themes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    colors = Column(JSON, nullable=False)  # color scheme
    typography = Column(JSON, nullable=False)  # font settings
    spacing = Column(JSON, nullable=False)  # layout spacing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="themes")

class DashboardExport(Base):
    """Dashboard export history."""
    __tablename__ = "dashboard_exports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    export_type = Column(String, nullable=False)
    format = Column(String, nullable=False)
    status = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="dashboard_exports")

class DashboardSearch(Base):
    """Dashboard search history."""
    __tablename__ = "dashboard_searches"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(String, nullable=False)
    filters = Column(JSON, default={})
    results_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="dashboard_searches")

class DashboardNotification(Base):
    """Model for dashboard notifications."""
    __tablename__ = "dashboard_notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="dashboard_notifications") 