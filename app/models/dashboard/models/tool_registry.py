"""
Tool registry model.
"""

from app.models.shared_base import SharedBase
from sqlalchemy import Column, String, JSON, Boolean, ForeignKey, Table, DateTime, Integer, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# Association table for user-tool relationships
user_tools = Table(
    'user_tools',
    SharedBase.metadata,
    Column('user_id', Integer, ForeignKey("users.id"), primary_key=True),
    Column('tool_id', Integer, ForeignKey("dashboard_tools.id"), primary_key=True),
    extend_existing=True
)

class Tool(SharedBase):
    __tablename__ = "dashboard_tool_registry"
    __table_args__ = {'extend_existing': True}

class DashboardUserTool(SharedBase):
    __tablename__ = "dashboard_user_tool_settings"
    __table_args__ = {'extend_existing': True} 