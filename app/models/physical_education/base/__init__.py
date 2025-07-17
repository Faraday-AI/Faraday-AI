"""
Base Models Package

This package exports base models and utilities for physical education models.
DEPRECATED: Use app.models.base and app.models.mixins instead.
"""

import warnings
from app.models.base import Base, BaseModel
from app.models.mixins import TimestampedMixin

from .base import (
    BaseResponseModel,
    BaseCreateModel,
    BaseUpdateModel,
    validate_string_field,
    validate_list_field,
    validate_dict_field
)

warnings.warn(
    "app.models.physical_education.base is deprecated. Use app.models.base and app.models.mixins instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backward compatibility
TimestampMixin = TimestampedMixin
BaseModelMixin = BaseModel

__all__ = [
    'Base',
    'BaseModel',
    'BaseModelMixin',
    'TimestampMixin',
    'TimestampedMixin',
    'BaseResponseModel',
    'BaseCreateModel',
    'BaseUpdateModel',
    'validate_string_field',
    'validate_list_field',
    'validate_dict_field'
] 