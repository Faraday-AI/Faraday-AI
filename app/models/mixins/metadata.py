"""
Metadata Mixin

This module provides metadata functionality for models.
"""

from sqlalchemy import Column, JSON

class MetadataMixin:
    """Mixin for models that require metadata storage."""
    
    __abstract__ = True
    
    _metadata = Column('metadata', JSON, nullable=True)  # Use _metadata internally to avoid conflict
    
    @property
    def metadata(self):
        """Property to access metadata for backward compatibility."""
        return self._metadata
    
    @metadata.setter
    def metadata(self, value):
        """Property setter for metadata."""
        self._metadata = value
    
    def dict(self):
        """Convert model to dictionary."""
        return {
            "metadata": self._metadata
        } 