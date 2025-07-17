"""
Named Mixin

This module provides name and description functionality for models.
"""

from sqlalchemy import Column, String

class NamedMixin:
    """Mixin for models that require a name field."""
    
    __abstract__ = True
    
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    def dict(self):
        """Convert model to dictionary."""
        return {
            "name": self.name,
            "description": self.description
        } 