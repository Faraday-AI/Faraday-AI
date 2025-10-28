"""
Beta Avatars Model

This module defines the BetaAvatar model for the beta teacher system.
"""

from sqlalchemy import Column, String, JSON, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.core.base import CoreBase
from app.models.user_management.avatar.types import AvatarType


class BetaAvatar(CoreBase):
    """Model for beta avatars in the teacher system."""
    __tablename__ = "beta_avatars"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False)
    image_url = Column(String(500))
    config = Column(JSON)
    voice_enabled = Column(Boolean, default=False)
    voice_config = Column(JSON)
    expression_config = Column(JSON)
    gesture_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "type": self.type,
            "image_url": self.image_url,
            "config": self.config,
            "voice_enabled": self.voice_enabled,
            "voice_config": self.voice_config,
            "expression_config": self.expression_config,
            "gesture_config": self.gesture_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

