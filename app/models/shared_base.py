"""
Shared Base Model

This module defines the shared base class for all models.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create a single shared base class
SharedBase = declarative_base()

# Re-export for convenience
__all__ = ['SharedBase'] 