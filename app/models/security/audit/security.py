"""
Security Audit Models

This module contains models for security auditing and logging.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.physical_education.base.base_class import Base

class SecurityAudit(Base):
    """Model for security audit logs."""
    
    __tablename__ = "security_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Relationships
    teacher = relationship("app.models.core.user.User", back_populates="security_audits")

class SecurityAuditLog(Base):
    """Model for general audit logs."""
    
    __tablename__ = "security_general_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    module = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="security_audit_logs") 