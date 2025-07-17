"""Cache models for the application."""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase

class CachePolicy(str, Enum):
    """Cache policy types."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    RANDOM = "random"  # Random replacement

class CacheStatus(str, Enum):
    """Cache entry status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    PENDING = "pending"

class CacheEntry(SharedBase):
    """Cache entry model."""
    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)
    ttl = Column(Integer)  # Time to live in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    status = Column(String, default=CacheStatus.ACTIVE)
    hits = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    extra_data = Column(JSON)

class CacheMetrics(SharedBase):
    """Cache metrics model."""
    __tablename__ = "cache_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    hits = Column(Integer, default=0)
    misses = Column(Integer, default=0)
    evictions = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    hit_ratio = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    extra_data = Column(JSON) 