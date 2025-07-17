"""
Security Policy Models

This module defines security policy models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict

from app.models.shared_base import SharedBase
from app.models.mixins import TimestampedMixin, StatusMixin, MetadataMixin
from ...core.core_models import SecurityLevel, SecurityStatus, SecurityAction, SecurityTrigger
from ...system.relationships import setup_security_relationships

# Re-export for backward compatibility
BaseModelMixin = SharedBase
TimestampMixin = TimestampedMixin

class SecurityPolicy(SharedBase, TimestampMixin, StatusMixin):
    """Model for security policies."""
    __tablename__ = "security_policies"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    policy_type = Column(String(50), nullable=False)
    rules = Column(JSONB, nullable=False)
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    policy_metadata = Column(JSONB)

    # Relationships
    rules_rel = relationship("app.models.security.policy.security.SecurityRule", back_populates="policy", cascade="all, delete-orphan")
    audits = relationship("app.models.security.policy.security.SecurityAudit", back_populates="policy", cascade="all, delete-orphan")
    incidents = relationship("SecurityIncident", back_populates="policy")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setup_security_relationships(self.__class__)

    def __repr__(self):
        return f"<SecurityPolicy {self.name}>"

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "name": self.name,
            "description": self.description,
            "rules": self.rules,
            "is_active": self.is_active,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class SecurityRule(SharedBase, TimestampMixin, StatusMixin):
    """Model for security rules."""
    __tablename__ = "security_rules"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("security_policies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    conditions = Column(JSONB, nullable=False)
    actions = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    rule_metadata = Column(JSONB)
    priority = Column(Integer, default=0)

    # Relationships
    policy = relationship("app.models.security.policy.security.SecurityPolicy", back_populates="rules_rel")
    audits = relationship("app.models.security.policy.security.SecurityAudit", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SecurityRule {self.name}>"

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "conditions": self.conditions,
            "actions": self.actions,
            "is_active": self.is_active,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class SecurityAudit(SharedBase, TimestampMixin):
    """Model for security audits."""
    __tablename__ = "policy_security_audits"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("security_policies.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("security_rules.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    audit_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(JSONB, nullable=False)
    audit_metadata = Column(JSONB)

    # Relationships
    policy = relationship("app.models.security.policy.security.SecurityPolicy", back_populates="audits")
    rule = relationship("app.models.security.policy.security.SecurityRule", back_populates="audits")

    def __repr__(self):
        return f"<SecurityAudit {self.id} - {self.audit_type}>"

class SecurityIncident(SharedBase, TimestampMixin, StatusMixin):
    """Model for security incidents."""
    __tablename__ = "security_incidents"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("security_policies.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    incident_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    resolution = Column(Text)
    incident_metadata = Column(JSONB)

    # Relationships
    policy = relationship("app.models.security.policy.security.SecurityPolicy", back_populates="incidents")

    def __repr__(self):
        return f"<SecurityIncident {self.id} - {self.incident_type}>"

# =====================================================================
# Dashboard Security Models (migrated from app/dashboard/models/security.py)
# =====================================================================

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# --- IPAllowlist ---
class IPAllowlist(SharedBase):
    """IP addresses that are explicitly allowed."""
    __tablename__ = "ip_allowlist"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False, unique=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    created_by_user = relationship("User", back_populates="ip_allowlist_entries")

# --- IPBlocklist ---
class IPBlocklist(SharedBase):
    """IP addresses that are explicitly blocked."""
    __tablename__ = "ip_blocklist"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False, unique=True)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    created_by_user = relationship("User", back_populates="ip_blocklist_entries")

# --- SecurityPolicyAuditLog ---
class SecurityPolicyAuditLog(SharedBase):
    """Audit log entries for security-relevant actions."""
    __tablename__ = "security_audit_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    details = Column(JSON, default={})

    user = relationship("User", back_populates="security_policy_audit_logs")

# --- Session ---
class Session(SharedBase):
    """User sessions with device and location information."""
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_info = Column(JSON, nullable=False)
    ip_address = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    termination_reason = Column(String)

    user = relationship("User", back_populates="sessions")

# --- Add relationships to User and APIKey models ---
# These should be added in the appropriate user and api_key model files, but are included here for reference:
# User.rate_limits = relationship("RateLimit", back_populates="user")
# User.ip_allowlist_entries = relationship("IPAllowlist", back_populates="created_by_user")
# User.ip_blocklist_entries = relationship("IPBlocklist", back_populates="created_by_user")
# User.security_policies = relationship("SecurityPolicy", back_populates="created_by_user")
# User.sessions = relationship("Session", back_populates="user")
# APIKey.rate_limits = relationship("RateLimit", back_populates="api_key") 