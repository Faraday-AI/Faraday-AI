"""
Core Base Models

This module defines the base models used throughout the application.
DEPRECATED: Use app.models.shared_base and app.models.mixins instead.
"""

import warnings
from app.models.shared_base import SharedBase
from app.models.mixins import NamedMixin, StatusMixin, MetadataMixin, TimestampedMixin, AuditableModel

warnings.warn(
    "app.models.core.base is deprecated. Use app.models.shared_base and app.models.mixins instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backward compatibility
CoreBase = SharedBase
Base = SharedBase

class BaseModel(CoreBase):
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

__all__ = ['CoreBase', 'BaseModel', 'NamedMixin', 'StatusMixin', 'MetadataMixin', 'TimestampedMixin', 'AuditableModel'] 