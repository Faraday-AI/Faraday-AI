"""
SQLAlchemy Base Models Module

This module defines the base SQLAlchemy models used throughout the application.
DEPRECATED: Use app.models.base and app.models.mixins instead.
"""

import warnings
from datetime import datetime
from typing import Dict, Any, Generator
from sqlalchemy import Column, Integer, DateTime, String, Boolean, JSON, create_engine
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from uuid import uuid4

from app.models.base import Base, BaseModel
from app.models.mixins import TimestampedMixin

warnings.warn(
    "app.models.physical_education.base.sqlalchemy_base is deprecated. Use app.models.base and app.models.mixins instead.",
    DeprecationWarning,
    stacklevel=2
)

# Alias BaseModel as BaseModelMixin for backward compatibility
BaseModelMixin = BaseModel

# Re-export for backward compatibility
__all__ = ['Base', 'BaseModel', 'BaseModelMixin', 'TimestampedMixin']

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./faraday.db")

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 