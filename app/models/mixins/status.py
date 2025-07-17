"""
Status Mixin

This module provides status tracking functionality for models.
"""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from enum import Enum

class BaseStatus(str, Enum):
    """Base status options."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class StatusMixin:
    """Mixin for models that require status tracking."""
    
    __abstract__ = True
    
    status = Column(SQLEnum(BaseStatus, name='base_status_enum'), nullable=False, default=BaseStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    
    def dict(self):
        """Convert model to dictionary."""
        return {
            "status": self.status,
            "is_active": self.is_active
        } 