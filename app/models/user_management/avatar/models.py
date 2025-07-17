"""
Avatar Models

This module defines avatar-related models for user management.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, JSON, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.core.base import CoreBase
from app.db.mixins import MetadataMixin
from app.models.user_management.avatar.types import AvatarType, AvatarStyle

class UserAvatar(CoreBase, MetadataMixin):
    """Model for user avatars."""
    __tablename__ = "user_avatars"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("avatar_templates.id"), nullable=True)
    avatar_type = Column(SQLEnum(AvatarType, name='avatar_type_enum'), nullable=False)
    style = Column(SQLEnum(AvatarStyle, name='avatar_style_enum'), nullable=False)
    avatar_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="avatars")
    template = relationship("AvatarTemplate", back_populates="avatars")
    customizations = relationship("app.models.user_management.avatar.models.AvatarCustomization", back_populates="avatar", overlaps="avatar,customizations")

class AvatarCustomization(CoreBase, MetadataMixin):
    """Model for avatar customizations."""
    __tablename__ = "user_avatar_customizations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(Integer, ForeignKey("user_avatars.id"), nullable=False)
    customization_type = Column(String, nullable=False)
    customization_value = Column(JSON, nullable=False)
    customization_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    avatar = relationship("UserAvatar", back_populates="customizations", overlaps="avatar,customizations")

class AvatarTemplate(CoreBase, MetadataMixin):
    """Model for avatar templates."""
    __tablename__ = "avatar_templates"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    template_data = Column(JSON, nullable=False)
    template_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    avatars = relationship("UserAvatar", back_populates="template") 