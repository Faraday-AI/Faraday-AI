"""
Base Class for Physical Education Models

This module provides the base class for physical education models.
DEPRECATED: Use app.models.shared_base instead.
"""

import warnings
from app.models.shared_base import SharedBase

warnings.warn(
    "app.models.physical_education.base.base_class is deprecated. Use app.models.shared_base instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backward compatibility
PEBase = SharedBase
Base = SharedBase 