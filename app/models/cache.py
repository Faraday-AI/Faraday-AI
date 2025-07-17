"""Cache models for the application."""

import enum
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.core.base import BaseModel

class CacheStatus(str, enum.Enum):
    """Status of cache entries."""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    PENDING = "pending"

class CachePolicy(BaseModel):
    """Model for cache policies."""
    __tablename__ = "cache_policies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    ttl = Column(Integer)  # Time to live in seconds
    max_size = Column(Integer)  # Maximum size in bytes
    priority = Column(String)  # One of CacheLevel values
    policy_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entries = relationship("CacheEntry", back_populates="policy")

class CacheEntry(BaseModel):
    """Model for cache entries."""
    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False, unique=True)
    value = Column(JSON)
    policy_id = Column(Integer, ForeignKey("cache_policies.id"))
    status = Column(String)  # One of CacheStatus values
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    entry_metadata = Column(JSON, default=dict)

    # Relationships
    policy = relationship("CachePolicy", back_populates="entries")
    metrics = relationship("CacheMetrics", back_populates="entry")

class CacheMetrics(BaseModel):
    """Model for cache metrics."""
    __tablename__ = "cache_metrics"

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("cache_entries.id"))
    hits = Column(Integer, default=0)
    misses = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    size_bytes = Column(Integer)
    metrics_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entry = relationship("CacheEntry", back_populates="metrics") 