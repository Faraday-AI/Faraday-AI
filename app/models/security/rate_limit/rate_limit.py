"""Rate limit models for the application."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship

from app.models.security.base import Base as SecurityBase
from app.models.physical_education.pe_enums.pe_types import (
    RateLimitType,
    RateLimitLevel,
    RateLimitStatus,
    RateLimitTrigger
)

class RateLimit(SecurityBase):
    """Model for rate limiting."""
    __tablename__ = "rate_limits"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    limit = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)  # Period in seconds
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_key = relationship("app.models.security.api_key.api_key.APIKey", back_populates="rate_limits")
    policies = relationship("app.models.security.rate_limit.rate_limit.RateLimitPolicy", back_populates="rate_limit")
    metrics = relationship("app.models.security.rate_limit.rate_limit.RateLimitMetrics", back_populates="rate_limit")

    def __repr__(self):
        return f"<RateLimit {self.endpoint}>"

class RateLimitPolicy(SecurityBase):
    """Model for rate limit policies."""
    __tablename__ = "rate_limit_policies"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    rate_limit_id = Column(Integer, ForeignKey("rate_limits.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    trigger = Column(SQLEnum(RateLimitTrigger, name='rate_limit_trigger_enum'), nullable=False)
    action = Column(String, nullable=False)
    parameters = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rate_limit = relationship("app.models.security.rate_limit.rate_limit.RateLimit", back_populates="policies")

    def __repr__(self):
        return f"<RateLimitPolicy {self.name}>"

class RateLimitMetrics(SecurityBase):
    """Model for rate limit metrics."""
    __tablename__ = "rate_limit_metrics"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    rate_limit_id = Column(Integer, ForeignKey("rate_limits.id"), nullable=False)
    window_start = Column(DateTime, nullable=False)
    request_count = Column(Integer, default=0)
    violation_count = Column(Integer, default=0)
    average_latency = Column(Float)
    max_latency = Column(Float)
    burst_count = Column(Integer, default=0)
    metrics_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rate_limit = relationship("app.models.security.rate_limit.rate_limit.RateLimit", back_populates="metrics")

    def __repr__(self):
        return f"<RateLimitMetrics {self.rate_limit_id}>"

class RateLimitLog(SecurityBase):
    __tablename__ = "rate_limit_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    api_key = relationship("app.models.security.api_key.api_key.APIKey", back_populates="rate_limit_logs")

    def __repr__(self):
        return f"<RateLimitLog {self.endpoint}>" 