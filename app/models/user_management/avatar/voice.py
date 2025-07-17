"""
Voice Models

This module defines voice-related models for user avatars.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, JSON, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.core.base import CoreBase
from app.db.mixins import MetadataMixin
from app.models.user_management.avatar.types import VoiceProvider

class VoicePreference(CoreBase, MetadataMixin):
    """Model for voice preferences."""
    __tablename__ = "user_management_voice_preferences"

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    voice_id = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    speed = Column(Integer, default=100)  # Percentage
    pitch = Column(Integer, default=100)  # Percentage
    provider = Column(SQLEnum(VoiceProvider, name='voice_provider_enum'), nullable=False)
    style = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    avatar = relationship("Avatar", back_populates="voice_preferences")
    user = relationship("User", back_populates="voice_preferences")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "avatar_id": self.avatar_id,
            "user_id": self.user_id,
            "voice_id": self.voice_id,
            "language": self.language,
            "speed": self.speed,
            "pitch": self.pitch,
            "provider": self.provider.value if self.provider else None,
            "style": self.style,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Voice(CoreBase, MetadataMixin):
    """Model for avatar voices."""
    __tablename__ = "voices"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("voice_templates.id"), nullable=True)
    voice_type = Column(String, nullable=False)
    voice_settings = Column(JSON, nullable=True)
    voice_metadata = Column(JSON, nullable=True)

    # Relationships
    avatar = relationship("Avatar", back_populates="voices")
    user = relationship("User", back_populates="voices")
    template = relationship("VoiceTemplate", back_populates="voices")

class VoiceTemplate(CoreBase, MetadataMixin):
    """Model for voice templates."""
    __tablename__ = "voice_templates"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    voice_settings = Column(JSON, nullable=False)
    template_metadata = Column(JSON, nullable=True)

    # Relationships
    voices = relationship("Voice", back_populates="template") 