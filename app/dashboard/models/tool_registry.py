"""
Tool registry model.
"""

from app.models.shared_base import SharedBase as Base
from sqlalchemy import Column, String, JSON, Boolean, ForeignKey, Table, DateTime, Integer, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# Association table for user-tool relationships
user_tools = Table(
    'user_tools',
    Base.metadata,
    Column('user_id', Integer, ForeignKey("users.id"), primary_key=True),
    Column('tool_id', Integer, ForeignKey("dashboard_tools.id"), primary_key=True),
    extend_existing=True
)

class Tool(Base):
    __tablename__ = "dashboard_tools"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    function_schema = Column(JSON)
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    version = Column(String)
    configuration = Column(JSON)
    validation_schema = Column(JSON)  # Schema for validating function inputs
    example_usage = Column(JSON)  # Example usage patterns
    rate_limit = Column(JSON)  # Rate limiting configuration
    error_handling = Column(JSON)  # Error handling configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Avatar-related fields
    avatar_type = Column(String, default="static")  # static, animated, 3d
    avatar_url = Column(String)  # URL to avatar image/asset
    avatar_config = Column(JSON)  # Configuration for animated/3D avatars
    voice_enabled = Column(Boolean, default=False)
    voice_config = Column(JSON)  # Voice configuration (provider, voice_id, etc.)
    avatar_id = Column(Integer, ForeignKey('avatars.id'), nullable=True)  # Foreign key to avatars table
    
    # Relationships
    users = relationship("User", secondary=user_tools, back_populates="tools")
    avatar = relationship("app.models.user_management.avatar.base.Avatar", back_populates="tool", uselist=False)
    user_settings = relationship("UserTool", back_populates="tool")
    feedback_user_settings = relationship("app.models.feedback.tools.user_tool.FeedbackUserTool", back_populates="tool")

class UserTool(Base):
    __tablename__ = "user_tool_settings"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("dashboard_tools.id"), primary_key=True)
    is_enabled = Column(Boolean, default=True)
    settings = Column(JSON)
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)
    rate_limit_remaining = Column(Integer)
    rate_limit_reset = Column(DateTime)
    error_count = Column(Integer, default=0)
    last_error = Column(DateTime)
    last_success = Column(DateTime)
    
    # Avatar customization
    avatar_customization = Column(JSON)  # User-specific avatar settings
    voice_preferences = Column(JSON)  # User-specific voice settings
    
    # Relationships
    user = relationship("User", back_populates="tool_settings")
    tool = relationship("app.dashboard.models.tool_registry.Tool", back_populates="user_settings") 