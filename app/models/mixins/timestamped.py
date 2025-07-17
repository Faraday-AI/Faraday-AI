"""
Timestamped Mixin

This module provides timestamp tracking functionality for models.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import Column, DateTime, Integer

class TimestampedMixin:
    """Mixin for models with detailed timestamps."""
    
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    scheduled_deletion_at = Column(DateTime, nullable=True)
    retention_period = Column(Integer, nullable=True)  # in days
    
    def mark_accessed(self) -> None:
        """Update last accessed timestamp."""
        self.last_accessed_at = datetime.utcnow()
    
    def archive(self) -> None:
        """Archive the record."""
        self.archived_at = datetime.utcnow()
    
    def soft_delete(self, retention_days: Optional[int] = None) -> None:
        """Soft delete the record with optional retention period."""
        self.deleted_at = datetime.utcnow()
        if retention_days:
            self.retention_period = retention_days
            self.scheduled_deletion_at = datetime.utcnow() + timedelta(days=retention_days)
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
            "scheduled_deletion_at": self.scheduled_deletion_at.isoformat() if self.scheduled_deletion_at else None,
            "retention_period": self.retention_period
        } 