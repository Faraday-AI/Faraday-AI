"""
Dashboard User Models

This module defines the database models for dashboard users and related functionality
in the Faraday AI Dashboard.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.shared_base import SharedBase
from .association_tables import gpt_sharing

class UserRole(enum.Enum):
    """Enumeration of user roles."""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    STAFF = "staff"
    # Extensible for future roles

class DashboardUser(SharedBase):
    """Model for storing dashboard user information."""
    __tablename__ = "dashboard_users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    # Link to core user system
    core_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Profile information
    profile_picture = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    
    # Preferences
    preferences = Column(JSON, default={})
    notification_settings = Column(JSON, default={})
    
    # Relationships
    core_user = relationship("app.models.core.user.User", back_populates="dashboard_user", foreign_keys=[core_user_id])
    contexts = relationship("app.dashboard.models.context.GPTContext", back_populates="user")
    context_templates = relationship("ContextTemplate", back_populates="created_by_user")
    projects = relationship("DashboardProject", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    # gpt_definitions = relationship("app.dashboard.models.gpt_models.GPTDefinition", back_populates="user")
    dashboard_gpt_subscriptions = relationship("app.dashboard.models.gpt_models.DashboardGPTSubscription", back_populates="user")
    gpt_usage = relationship("app.dashboard.models.gpt_models.GPTUsage", back_populates="user")
    gpt_integrations = relationship("app.dashboard.models.gpt_models.GPTIntegration", back_populates="user")
    gpt_analytics = relationship("app.dashboard.models.gpt_models.GPTAnalytics", back_populates="user")
    gpt_feedback = relationship("app.dashboard.models.gpt_models.GPTFeedback", back_populates="user")
    gpt_performance = relationship("app.dashboard.models.gpt_models.GPTPerformance", back_populates="user")
    feedback = relationship("app.dashboard.models.feedback.Feedback", back_populates="user")
    dashboard_team_memberships = relationship("app.dashboard.models.team.DashboardTeamMember", back_populates="user")
    ai_suites = relationship("AISuite", back_populates="user")
    assigned_tools = relationship(
        "AITool", 
        secondary="tool_assignments",
        primaryjoin="DashboardUser.id == tool_assignments.c.user_id",
        secondaryjoin="tool_assignments.c.tool_id == AITool.id",
        back_populates="assigned_users"
    )
    tool_usage_logs = relationship("ToolUsageLog", back_populates="user")
    filters = relationship("Filter", back_populates="user")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True) 