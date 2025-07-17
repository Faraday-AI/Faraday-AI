"""
Dashboard Models

This module defines the database models for dashboard widgets and related functionality.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.shared_base import SharedBase

class WidgetType(enum.Enum):
    """Enumeration of dashboard widget types."""
    CHART = "chart"
    METRIC = "metric"
    TABLE = "table"
    LIST = "list"
    CALENDAR = "calendar"
    MAP = "map"
    CUSTOM = "custom"

class WidgetLayout(enum.Enum):
    """Enumeration of widget layout positions."""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    FULL_WIDTH = "full_width"

class DashboardWidget(SharedBase):
    """Model for dashboard widgets."""
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Widget configuration
    widget_type = Column(Enum(WidgetType, name='widget_type_enum'), nullable=False)
    layout_position = Column(Enum(WidgetLayout, name='widget_layout_enum'), nullable=False)
    size = Column(JSON, nullable=False)  # e.g., {"width": 2, "height": 2}
    configuration = Column(JSON, nullable=False)  # Widget-specific configuration
    refresh_interval = Column(Integer, nullable=True)  # in seconds
    
    # Widget state
    is_active = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)
    last_refresh = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dashboard_widgets")
    project = relationship("DashboardProject", back_populates="dashboard_widgets")
    organization = relationship("Organization", back_populates="dashboard_widgets")
    dashboard = relationship("Dashboard", back_populates="widgets")

    # Additional metadata
    meta_data = Column(JSON)

class Dashboard(SharedBase):
    """Model for dashboards."""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Dashboard configuration
    layout = Column(JSON, nullable=False)  # Dashboard layout configuration
    theme = Column(String, nullable=True)
    refresh_interval = Column(Integer, nullable=True)  # in seconds
    
    # Dashboard state
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    last_refresh = Column(DateTime, nullable=True)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dashboards")
    project = relationship("DashboardProject", back_populates="dashboards")
    organization = relationship("Organization", back_populates="dashboards")
    widgets = relationship("DashboardWidget", back_populates="dashboard")
    
    # Additional metadata
    meta_data = Column(JSON)

class DashboardShare(SharedBase):
    """Model for dashboard sharing configurations."""
    __tablename__ = "dashboard_shares"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    share_type = Column(String, nullable=False)  # link, embed, export
    permissions = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Optional foreign keys
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_shares")
    project = relationship("DashboardProject", back_populates="dashboard_shares")
    organization = relationship("Organization", back_populates="dashboard_shares")
    
    # Additional metadata
    meta_data = Column(JSON)

class DashboardFilter(SharedBase):
    """Model for dashboard filters."""
    __tablename__ = "dashboard_filters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filter_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False, default={})
    applied_to = Column(JSON, nullable=False, default=[])  # List of widget IDs this filter applies to
    
    # Optional foreign keys
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="dashboard_filters")
    project = relationship("DashboardProject", back_populates="dashboard_filters")
    organization = relationship("Organization", back_populates="dashboard_filters")
    
    # Additional metadata
    meta_data = Column(JSON)

class DashboardAnalytics(SharedBase):
    """Analytics data for dashboard usage."""
    __tablename__ = "dashboard_analytics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    metrics = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    period = Column(String)  # daily, weekly, monthly
    gpt_usage = Column(JSON)  # Added detailed GPT usage tracking
    api_calls = Column(JSON)  # Added API call tracking
    error_logs = Column(JSON)  # Added error logging

    # Relationships
    user = relationship("DashboardUser") 