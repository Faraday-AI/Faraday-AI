"""
AI Tool Model

This module defines the AITool model for managing AI tools and capabilities.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Table, ForeignKeyConstraint, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.core.base import CoreBase

# Association table for tool assignments
tool_assignments = Table(
    "tool_assignments",
    CoreBase.metadata,
    Column("tool_id", Integer, ForeignKey("ai_tools.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("dashboard_users.id"), primary_key=True),
    Column("assigned_by", Integer, ForeignKey("dashboard_users.id")),
    Column("assigned_at", DateTime, default=datetime.utcnow),
    Column("expires_at", DateTime),
    extend_existing=True
)

class AITool(CoreBase):
    """Model for AI tools."""
    __tablename__ = "ai_tools"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    suite_id = Column(Integer, ForeignKey("ai_suites.id"))
    tool_type = Column(String, nullable=False)
    configuration = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    suite = relationship("AISuite", back_populates="tools")
    assigned_users = relationship(
        "DashboardUser",
        secondary="tool_assignments",
        primaryjoin="AITool.id == tool_assignments.c.tool_id",
        secondaryjoin="tool_assignments.c.user_id == DashboardUser.id",
        back_populates="assigned_tools"
    )
    marketplace_listing = relationship("MarketplaceListing", back_populates="tool", uselist=False)
    usage_logs = relationship("ToolUsageLog", back_populates="tool")

    def __repr__(self):
        return f"<AITool {self.name}>"

    # Note: Foreign key constraints are already defined in the Table definition above
    # No need for additional __declare_last__ method 