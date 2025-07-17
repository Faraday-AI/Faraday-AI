"""
User Preferences Management Models

This module defines the database models for user preferences and settings
in the Faraday AI system.
"""

from sqlalchemy import Column, String, JSON, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Integer, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.core.base import CoreBase, BaseModel, MetadataMixin
from app.db.mixins import StatusMixin
from app.models.user_management.preferences.types import PreferenceType
from app.dashboard.models.user_preferences import UserPreferences

# Many-to-many relationship table for user preference templates
user_preference_template_assignments = Table(
    'user_preference_template_assignments',
    CoreBase.metadata,
    Column('user_id', Integer, ForeignKey("users.id")),
    Column('template_id', Integer, ForeignKey('user_preference_templates.id'))
)

# Re-export the UserPreferences class
__all__ = ['UserPreferences', 'UserPreference', 'UserPreferenceCategory', 'UserPreferenceTemplate']

class UserPreference(CoreBase):
    """Model for user preferences."""
    __tablename__ = "user_management_preferences"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("user_preference_categories.id"), nullable=True)
    type = Column(SQLEnum(PreferenceType, name='preference_type_enum'), nullable=False)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_management_preferences", overlaps="preferences")
    category = relationship("UserPreferenceCategory", back_populates="preferences")

    def dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "type": self.type.value if self.type else None,
            "config": self.config,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class UserPreferenceCategory(CoreBase):
    """Model for user preference categories."""
    __tablename__ = "user_preference_categories"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_metadata = Column(JSON, nullable=True)

    # Relationships
    preferences = relationship("UserPreference", back_populates="category")

class UserPreferenceTemplate(CoreBase):
    """Model for user preference templates."""
    __tablename__ = "user_preference_templates"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    template_data = Column(JSON, nullable=False)
    template_metadata = Column(JSON, nullable=True)

    # Relationships
    users = relationship("User", secondary="user_preference_template_assignments", back_populates="preference_templates") 