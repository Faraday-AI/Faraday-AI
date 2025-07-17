"""
Circuit Breaker Models

This module defines models for the circuit breaker pattern implementation.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.core.base import CoreBase
from app.db.mixins import MetadataMixin

class CircuitBreaker(CoreBase, MetadataMixin):
    """Model for circuit breaker configuration."""
    __tablename__ = "circuit_breakers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    service_name = Column(String, nullable=False)
    failure_threshold = Column(Integer, nullable=False)
    reset_timeout = Column(Integer, nullable=False)  # in seconds
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    breaker_metadata = Column(JSON, nullable=True)

    # Relationships
    states = relationship("CircuitBreakerState", back_populates="circuit_breaker")
    failures = relationship("CircuitBreakerFailure", back_populates="circuit_breaker")

class CircuitBreakerState(CoreBase, MetadataMixin):
    """Model for circuit breaker state."""
    __tablename__ = "circuit_breaker_states"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    circuit_breaker_id = Column(Integer, ForeignKey("circuit_breakers.id"))
    state = Column(String, nullable=False)  # OPEN, CLOSED, HALF_OPEN
    last_state_change = Column(DateTime, nullable=False)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    state_metadata = Column(JSON, nullable=True)

    # Relationships
    circuit_breaker = relationship("CircuitBreaker", back_populates="states")

class CircuitBreakerFailure(CoreBase, MetadataMixin):
    """Model for circuit breaker failures."""
    __tablename__ = "circuit_breaker_failures"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    circuit_breaker_id = Column(Integer, ForeignKey("circuit_breakers.id"))
    error_type = Column(String, nullable=False)
    error_message = Column(String, nullable=True)
    occurred_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    failure_metadata = Column(JSON, nullable=True)

    # Relationships
    circuit_breaker = relationship("CircuitBreaker", back_populates="failures") 