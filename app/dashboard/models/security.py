"""
Security Models

This module defines security-related models for the dashboard.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase

class APIKeyInfo(BaseModel):
    """Pydantic model for API key information."""
    key_id: str
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class RoleInfo(BaseModel):
    """Pydantic model for role information."""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class DashboardAPIKey(SharedBase):
    """Model for dashboard API keys."""
    
    __tablename__ = "dashboard_api_keys"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    key_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    hashed_secret = Column(String(100), nullable=False)
    permissions = Column(JSON)
    expires_at = Column(DateTime)
    revoked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("app.models.core.user.User", foreign_keys=[user_id], back_populates="dashboard_api_keys")

class DashboardRateLimit(SharedBase):
    """Model for dashboard rate limits."""
    
    __tablename__ = "dashboard_rate_limits"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(100), nullable=False)
    requests_per_minute = Column(Integer, nullable=False)
    burst_size = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    api_key_id = Column(Integer, ForeignKey("dashboard_api_keys.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IPAllowlist(SharedBase):
    """Model for IP allowlist."""
    
    __tablename__ = "dashboard_ip_allowlist"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IPBlocklist(SharedBase):
    """Model for IP blocklist."""
    
    __tablename__ = "dashboard_ip_blocklist"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(50), nullable=False, unique=True)
    reason = Column(Text, nullable=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(SharedBase):
    """Model for audit logs."""
    
    __tablename__ = "dashboard_audit_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SecurityPolicy(SharedBase):
    """Model for security policies."""
    
    __tablename__ = "dashboard_security_policies"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    policy_type = Column(String(50), nullable=False)
    rules = Column(JSON, nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Session(SharedBase):
    """Model for user sessions."""
    
    __tablename__ = "dashboard_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_info = Column(JSON)
    ip_address = Column(String(50))
    last_active = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    terminated_at = Column(DateTime)
    termination_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityMetrics(BaseModel):
    """Pydantic model for security metrics."""
    total_api_keys: int
    active_api_keys: int
    total_roles: int
    total_permissions: int
    alerts: Optional[List[Dict[str, Any]]] = None
    access_logs: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True) 