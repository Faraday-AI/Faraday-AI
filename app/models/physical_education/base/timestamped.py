"""
Timestamped model functionality.

This module provides timestamp tracking functionality for models.
DEPRECATED: Use app.models.mixins.timestamped.TimestampedMixin instead.
"""

import warnings
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import Column, DateTime, Integer

from app.models.base import Base
from app.models.mixins import TimestampedMixin as NewTimestampedMixin

warnings.warn(
    "app.models.physical_education.base.timestamped is deprecated. "
    "Use app.models.mixins.timestamped.TimestampedMixin instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backward compatibility
TimestampedMixin = NewTimestampedMixin

class TimestampedModel(Base, TimestampedMixin):
    """Model with timestamp tracking functionality."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return super().dict() 