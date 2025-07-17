"""
Base Models

This module defines the base models used throughout the application.
"""

from app.models.shared_base import SharedBase
from app.models.mixins import NamedMixin, StatusMixin, MetadataMixin, TimestampedMixin

# Re-export SharedBase as Base for backward compatibility
Base = SharedBase

class BaseModel(Base):
    """Base model with common functionality"""
    __abstract__ = True

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create model instance from dictionary"""
        return cls(**data)

# Re-export mixins for convenience
__all__ = ['Base', 'BaseModel', 'NamedMixin', 'StatusMixin', 'MetadataMixin', 'TimestampedMixin'] 