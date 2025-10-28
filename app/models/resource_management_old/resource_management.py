"""
Resource Management Models

This module defines the database models for resource monitoring, optimization,
and sharing in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.physical_education.base.base_class import Base
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class ResourceType(str, enum.Enum):
    """Types of resources that can be monitored."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"

class ResourceMetric(str, enum.Enum):
    """Types of metrics that can be collected."""
    USAGE = "usage"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    COST = "cost"
    EFFICIENCY = "efficiency"

class Phase11ResourceUsage(BaseModel, MetadataMixin):
    """Model for storing resource usage metrics."""
    __tablename__ = "resource_management_usage"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resource_usage")
    # project = relationship("Project", back_populates="resource_usage")
    # organization = relationship("Organization", back_populates="resource_usage")

class Phase11ResourceThreshold(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource usage thresholds."""
    __tablename__ = "resource_thresholds"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    threshold_value = Column(Float, nullable=False)
    threshold_type = Column(String, nullable=False)  # 'warning' or 'critical'
    action = Column(String, nullable=False)  # 'notify', 'scale', 'alert', etc.
    is_active = Column(Boolean, default=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resource_thresholds")
    # project = relationship("Project", back_populates="resource_thresholds")
    # organization = relationship("Organization", back_populates="resource_thresholds")

class Phase11ResourceOptimization(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource optimization recommendations."""
    __tablename__ = "resource_optimizations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    current_value = Column(Float, nullable=False)
    recommended_value = Column(Float, nullable=False)
    potential_savings = Column(Float)
    confidence_score = Column(Float)
    recommendation = Column(String, nullable=False)
    applied_at = Column(DateTime)
    applied = Column(Boolean, default=False)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resource_optimizations")
    # project = relationship("Project", back_populates="resource_optimizations")
    # organization = relationship("Organization", back_populates="resource_optimizations")

class Phase11ResourceSharing(BaseModel, StatusMixin, MetadataMixin):
    """Model for managing resource sharing between users and projects."""
    __tablename__ = "resource_management_sharing"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    
    # Sharing configuration
    sharing_type = Column(String, nullable=False)  # 'user', 'project', 'organization'
    sharing_permissions = Column(JSON, nullable=False)  # e.g., {"read": true, "write": false}
    sharing_scope = Column(String, nullable=False)  # 'public', 'private', 'restricted'
    
    # Time management
    expires_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_with_project_id = Column(Integer, ForeignKey("dashboard_projects.id"), nullable=True)
    shared_with_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_resources")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id], back_populates="shared_resources")
    # shared_with_project = relationship("Project", back_populates="shared_resources")
    # shared_with_organization = relationship("Organization", back_populates="shared_resources")

class Phase11OptimizationEvent(BaseModel, StatusMixin, MetadataMixin):
    """Model for tracking optimization events and their status."""
    __tablename__ = "optimization_events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)  # 'threshold_breach', 'optimization_applied', 'resource_shared', etc.
    severity = Column(String, nullable=False)  # 'info', 'warning', 'critical'
    
    # Resource information
    resource_id = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    
    # Event details
    description = Column(String, nullable=False)
    action_taken = Column(String, nullable=True)
    action_result = Column(String, nullable=True)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Relationships
    user = relationship("User", back_populates="optimization_events")
    # project = relationship("Project", back_populates="optimization_events")
    # organization = relationship("Organization", back_populates="optimization_events") 