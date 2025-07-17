"""
Tool Usage Log Model

This module defines the ToolUsageLog model for logging tool usage.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float, Numeric, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

class ToolUsageLog(Base):
    """Model for logging tool usage."""
    __tablename__ = "dashboard_tool_usage_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("ai_tools.id"), nullable=False)
    session_id = Column(String)
    module_id = Column(String)
    action = Column(String, nullable=False)
    parameters = Column(JSON)
    credits_used = Column(Numeric(10, 2), default=0)
    status = Column(String)
    error_message = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration = Column(Float)
    usage_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("DashboardUser", back_populates="tool_usage_logs")
    tool = relationship("AITool", back_populates="usage_logs") 