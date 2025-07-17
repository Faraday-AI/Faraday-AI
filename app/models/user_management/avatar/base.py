"""
Avatar Base Model

This module defines the base Avatar model.
"""

from sqlalchemy import Column, String, JSON, Boolean, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import CoreBase
from app.db.mixins import StatusMixin, MetadataMixin
from app.models.user_management.avatar.types import AvatarType

class Avatar(CoreBase):
    """Base model for avatars."""
    __tablename__ = "avatars"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(AvatarType, name='avatar_type_enum'), nullable=False)
    url = Column(String, nullable=False)
    config = Column(JSON)
    voice_enabled = Column(Boolean, default=False)
    voice_config = Column(JSON)
    expression_config = Column(JSON)
    gesture_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tool = relationship("app.dashboard.models.tool_registry.Tool", back_populates="avatar", uselist=False)
    user_profile = relationship("UserProfile", back_populates="avatar", uselist=False)
    customizations = relationship("app.models.user_management.avatar.customization.AvatarCustomization", back_populates="avatar")
    student_customizations = relationship("StudentAvatarCustomization", back_populates="avatar")
    voice_preferences = relationship("VoicePreference", back_populates="avatar")
    voices = relationship("Voice", back_populates="avatar")

    def dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value if self.type else None,
            "url": self.url,
            "config": self.config,
            "voice_enabled": self.voice_enabled,
            "voice_config": self.voice_config,
            "expression_config": self.expression_config,
            "gesture_config": self.gesture_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 