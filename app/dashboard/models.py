"""
Dashboard Database Models

This module defines the database models for the Faraday AI Dashboard,
including user management, GPT subscriptions, and project organization.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Table, Float, Numeric, Enum as SQLEnum, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.shared_base import SharedBase
from .organization_models import Organization, Department
from .models.user import DashboardUser, BillingTier, UserType
from .models.project import DashboardProject
from .models.gpt_models import (
    DashboardGPTSubscription,
    GPTVersion,
    GPTContext,
    GPTPerformance,
    GPTDefinition,
    GPTUsage,
    GPTIntegration,
    GPTAnalytics,
    GPTFeedback,
    GPTUsageHistory,
    ContextInteraction,
    SharedContext,
    ContextSummary,
    ContextTemplate,
    ContextBackup,
    ContextMetrics,
    ContextValidation,
    ContextOptimization
)

# Association table for GPT sharing
gpt_sharing = Table(
    "gpt_sharing",
    SharedBase.metadata,
    Column("gpt_id", Integer, ForeignKey("dashboard_gpt_subscriptions.id"), primary_key=True),
    Column("shared_with_user_id", Integer, ForeignKey("dashboard_users.id"), primary_key=True),
    Column("permissions", JSON),
    Column("created_at", DateTime, default=datetime.utcnow)
)

# Association table for GPT categories
gpt_categories = Table(
    "gpt_categories",
    SharedBase.metadata,
    Column("gpt_id", Integer, ForeignKey("dashboard_gpt_subscriptions.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("dashboard_categories.id"), primary_key=True)
)

class DashboardUser(SharedBase):
    """Model for dashboard users."""
    __tablename__ = "dashboard_users_legacy"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    permissions = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="dashboard_user")
    subscriptions = relationship("DashboardGPTSubscription", back_populates="user")
    contexts = relationship("GPTContext", back_populates="user")
    feedback = relationship("app.dashboard.models.feedback.Feedback", back_populates="user")

class ToolUsageLog(SharedBase):
    """Model for tool usage logs."""
    __tablename__ = "dashboard_tool_usage_logs_legacy"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("ai_tools.id"), nullable=False)
    usage_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("DashboardUser", back_populates="tool_usage_logs")
    tool = relationship("AITool", back_populates="usage_logs")

class MarketplaceListing(SharedBase):
    """Model for marketplace listings."""
    __tablename__ = "dashboard_marketplace_listings_legacy"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    tool_id = Column(Integer, ForeignKey("ai_tools.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)

    # Relationships
    tool = relationship("AITool", back_populates="marketplace_listings")

# New models for additional features
class Category(SharedBase):
    """Model for GPT categories."""
    __tablename__ = "dashboard_categories_legacy"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    gpts = relationship("GPTSubscription", secondary="gpt_categories", back_populates="categories")

class AuditLog(SharedBase):
    """Model for audit logging."""
    __tablename__ = "dashboard_general_audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(Integer, nullable=False)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("DashboardUser", back_populates="audit_logs")

class DashboardModels:
    """Namespace class for all dashboard models."""
    User = DashboardUser
    GPTSubscription = DashboardGPTSubscription
    Project = DashboardProject
    GPTPerformance = GPTPerformance
    Feedback = None  # Removed duplicate, use app.dashboard.models.feedback.Feedback
    AuditLog = AuditLog
    Organization = Organization
    Department = Department

    @classmethod
    def get_all_models(cls):
        """Get all model classes."""
        return [
            cls.User,
            cls.GPTSubscription,
            cls.Project,
            cls.GPTPerformance,
            cls.AuditLog,
            cls.Organization,
            cls.Department
        ]

# Re-export the models for convenience
__all__ = [] 