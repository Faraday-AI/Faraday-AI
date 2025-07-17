"""
Avatar Customization Model

This module defines the AvatarCustomization model for managing avatar customization settings.
"""

from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import CoreBase
from app.db.mixins import StatusMixin, MetadataMixin
from app.models.user_management.avatar.types import CustomizationType

class AvatarCustomization(CoreBase):
    """Model for avatar customization settings."""
    __tablename__ = "avatar_customizations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("avatars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scale = Column(Integer, default=100)  # Percentage
    position = Column(JSON)  # {x: float, y: float, z: float}
    rotation = Column(JSON)  # {x: float, y: float, z: float}
    color = Column(String)  # Hex color code
    opacity = Column(Integer, default=100)  # Percentage
    type = Column(SQLEnum(CustomizationType, name='customization_type_enum'), nullable=False)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    avatar = relationship("Avatar", back_populates="customizations")
    user = relationship("User", back_populates="avatar_customizations")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "id": self.id,
            "avatar_id": self.avatar_id,
            "user_id": self.user_id,
            "scale": self.scale,
            "position": self.position,
            "rotation": self.rotation,
            "color": self.color,
            "opacity": self.opacity,
            "type": self.type.value if self.type else None,
            "config": self.config,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 