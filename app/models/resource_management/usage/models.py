"""
Resource Usage Models

This module defines models for tracking resource usage.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.physical_education.base.base_class import Base
from app.models.core.base import BaseModel, MetadataMixin, StatusMixin
from app.models.resource_management.base import ResourceType, ResourceMetric

class ResourceUsage(BaseModel, StatusMixin, MetadataMixin):
    """Model for resource usage tracking."""
    __tablename__ = "resource_management_usage_models"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    usage_type = Column(String, nullable=False)
    usage_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resource_usage")
    # organization = relationship("Organization", back_populates="resource_usage")
    # resource = relationship("Resource", back_populates="usage")

class ResourceUsageLimit(BaseModel, StatusMixin, MetadataMixin):
    """Model for resource usage limits."""
    __tablename__ = "resource_usage_limits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    limit_type = Column(String, nullable=False)
    limit_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resource_usage_limits")
    # organization = relationship("Organization", back_populates="resource_usage_limits")
    # resource = relationship("Resource", back_populates="usage_limits")

class ResourceUsageAlert(BaseModel, StatusMixin, MetadataMixin):
    """Model for resource usage alerts."""
    __tablename__ = "resource_usage_alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    alert_type = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="resource_usage_alerts")
    # organization = relationship("Organization", back_populates="resource_usage_alerts")
    # resource = relationship("Resource", back_populates="usage_alerts") 