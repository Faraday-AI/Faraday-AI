"""
User Tool Model

This module defines the database model for user-specific tool settings in the Faraday AI system.
"""

from sqlalchemy import Column, String, JSON, Boolean, ForeignKey, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase

class FeedbackToolSettings(SharedBase):
    """Model for feedback tool settings and usage in feedback context."""
    __tablename__ = "feedback_tool_settings"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("dashboard_tools.id"), primary_key=True)
    is_enabled = Column(Boolean, default=True)
    settings = Column(JSON, nullable=True)
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    rate_limit_remaining = Column(Integer, nullable=True)
    rate_limit_reset = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)
    last_error = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Avatar customization
    avatar_customization = Column(JSON, nullable=True)  # User-specific avatar settings
    voice_preferences = Column(JSON, nullable=True)  # User-specific voice settings
    
    # Relationships
    # user = relationship("app.models.core.user.User", back_populates="tool_settings")
    tool = relationship("app.dashboard.models.tool_registry.Tool", back_populates="feedback_user_settings")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "user_id": self.user_id,
            "tool_id": self.tool_id,
            "is_enabled": self.is_enabled,
            "settings": self.settings,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset.isoformat() if self.rate_limit_reset else None,
            "error_count": self.error_count,
            "last_error": self.last_error.isoformat() if self.last_error else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "avatar_customization": self.avatar_customization,
            "voice_preferences": self.voice_preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 