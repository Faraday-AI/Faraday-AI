"""
Circuit Breaker Models

This module contains models for circuit breaker functionality.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum, Boolean, Float
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.physical_education.pe_enums.pe_types import (
    CircuitBreakerType,
    CircuitBreakerLevel,
    CircuitBreakerStatus,
    CircuitBreakerTrigger
)

class CircuitBreakerMetrics(SharedBase):
    """Metrics for circuit breaker performance."""
    __tablename__ = "circuit_breaker_metrics"

    id = Column(Integer, primary_key=True, index=True)
    circuit_breaker_id = Column(Integer, ForeignKey("circuit_breakers.id"))
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    total_latency = Column(Float, default=0.0)  # in milliseconds
    average_latency = Column(Float, default=0.0)  # in milliseconds
    max_latency = Column(Float, default=0.0)  # in milliseconds
    min_latency = Column(Float, default=0.0)  # in milliseconds
    error_rate = Column(Float, default=0.0)  # percentage
    success_rate = Column(Float, default=0.0)  # percentage
    last_updated = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)

    # Relationships
    circuit_breaker = relationship("CircuitBreaker", back_populates="metrics")

class CircuitBreakerPolicy(SharedBase):
    """Policy configuration for circuit breakers."""
    __tablename__ = "circuit_breaker_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(Enum(CircuitBreakerType, name='circuit_breaker_type_enum'), nullable=False)
    level = Column(Enum(CircuitBreakerLevel, name='circuit_breaker_level_enum'), nullable=False)
    is_active = Column(Boolean, default=True)
    failure_threshold = Column(Integer, nullable=False)
    reset_timeout = Column(Integer, nullable=False)  # in seconds
    half_open_timeout = Column(Integer)  # in seconds
    max_failures = Column(Integer)
    error_threshold = Column(Integer)
    success_threshold = Column(Integer)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    circuit_breakers = relationship("CircuitBreaker", back_populates="policy")

class CircuitBreaker(SharedBase):
    """Circuit breaker model for activity protection."""
    __tablename__ = "circuit_breakers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(Enum(CircuitBreakerType, name='circuit_breaker_type_enum'), nullable=False)
    level = Column(Enum(CircuitBreakerLevel, name='circuit_breaker_level_enum'), nullable=False)
    status = Column(Enum(CircuitBreakerStatus, name='circuit_breaker_status_enum'), nullable=False, default=CircuitBreakerStatus.CLOSED)
    trigger = Column(Enum(CircuitBreakerTrigger, name='circuit_breaker_trigger_enum'), nullable=False)
    threshold = Column(Integer, nullable=False)
    failure_count = Column(Integer, default=0)
    last_failure_time = Column(DateTime)
    last_success_time = Column(DateTime)
    reset_timeout = Column(Integer)  # in seconds
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity_id = Column(Integer, ForeignKey("activities.id"))
    activity = relationship("app.models.physical_education.activity.models.Activity", back_populates="circuit_breakers")
    policy_id = Column(Integer, ForeignKey("circuit_breaker_policies.id"))
    policy = relationship("CircuitBreakerPolicy", back_populates="circuit_breakers")
    metrics = relationship("CircuitBreakerMetrics", back_populates="circuit_breaker", uselist=False)

class CircuitBreakerHistory(SharedBase):
    """History of circuit breaker state changes."""
    __tablename__ = "circuit_breaker_history"

    id = Column(Integer, primary_key=True, index=True)
    circuit_breaker_id = Column(Integer, ForeignKey("circuit_breakers.id"))
    previous_status = Column(Enum(CircuitBreakerStatus))
    new_status = Column(Enum(CircuitBreakerStatus))
    trigger = Column(Enum(CircuitBreakerTrigger))
    failure_count = Column(Integer)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    circuit_breaker = relationship("CircuitBreaker", back_populates="history")

# Add relationships
CircuitBreaker.history = relationship("CircuitBreakerHistory", back_populates="circuit_breaker")

__all__ = [
    'CircuitBreaker',
    'CircuitBreakerHistory',
    'CircuitBreakerPolicy',
    'CircuitBreakerMetrics'
] 