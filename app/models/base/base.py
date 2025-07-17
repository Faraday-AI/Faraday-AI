"""
Base Models

This module provides core base classes and mixins.
DEPRECATED: Use app.models.base and app.models.mixins instead.
"""

import warnings
from app.models.base import Base, BaseModel
from app.models.mixins import NamedMixin, StatusMixin, MetadataMixin, TimestampedMixin

warnings.warn(
    "app.models.base.base is deprecated. Use app.models.base and app.models.mixins instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backward compatibility
__all__ = ['Base', 'BaseModel', 'NamedMixin', 'StatusMixin', 'MetadataMixin', 'TimestampedMixin'] 