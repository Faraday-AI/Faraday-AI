"""
Base Environmental Model

This module defines the base model for environmental data in the Faraday AI system.
DEPRECATED: Use app.models.base and app.models.mixins instead.
"""

import warnings
from app.models.base import BaseModel
from app.models.mixins import TimestampedMixin, MetadataMixin

warnings.warn(
    "app.models.environmental.base.base is deprecated. Use app.models.base and app.models.mixins instead.",
    DeprecationWarning,
    stacklevel=2
)

class EnvironmentalBaseModel(BaseModel, TimestampedMixin, MetadataMixin):
    """
    Base model for environmental data, including timestamps and metadata.
    """
    __abstract__ = True 