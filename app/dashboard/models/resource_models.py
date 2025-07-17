"""
Resource models for the dashboard.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.shared_base import SharedBase as Base

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

class DashboardResourceUsage(Base):
    """Model for storing dashboard resource usage metrics."""
    __tablename__ = "dashboard_resource_usage"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_resource_usage")

class DashboardResourceThreshold(Base):
    """Model for storing dashboard resource usage thresholds."""
    __tablename__ = "dashboard_resource_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    threshold_value = Column(Float, nullable=False)
    threshold_type = Column(String, nullable=False)  # 'warning' or 'critical'
    action = Column(String, nullable=False)  # 'notify', 'scale', 'alert', etc.
    meta_data = Column(JSON)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_resource_thresholds")

class DashboardResourceOptimization(Base):
    """Model for storing dashboard resource optimization recommendations."""
    __tablename__ = "dashboard_resource_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    current_value = Column(Float, nullable=False)
    recommended_value = Column(Float, nullable=False)
    potential_savings = Column(Float)
    confidence_score = Column(Float)
    recommendation = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, applied, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    applied_at = Column(DateTime)
    meta_data = Column(JSON)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    user = relationship("User", back_populates="dashboard_resource_optimizations")

class DashboardResourceSharing(Base):
    """Model for managing dashboard resource sharing between users and projects."""
    __tablename__ = "dashboard_resource_sharing"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    
    # Sharing configuration
    is_shared = Column(Boolean, default=False)
    sharing_type = Column(String, nullable=False)  # 'user', 'project', 'organization'
    sharing_permissions = Column(JSON, nullable=False)  # e.g., {"read": true, "write": false}
    sharing_scope = Column(String, nullable=False)  # 'public', 'private', 'restricted'
    
    # Timestamps
    shared_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Optional foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_with_project_id = Column(Integer, ForeignKey("dashboard_projects.id"), nullable=True)
    shared_with_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="dashboard_owned_resources")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id], back_populates="dashboard_shared_resources")
    
    # Additional metadata
    meta_data = Column(JSON)

class DashboardOptimizationEvent(Base):
    """Model for tracking dashboard optimization events and their status."""
    __tablename__ = "dashboard_optimization_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)  # 'threshold_breach', 'optimization_applied', 'resource_shared', etc.
    status = Column(String, nullable=False)  # 'pending', 'in_progress', 'completed', 'failed'
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
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Relationships
    user = relationship("User", back_populates="dashboard_optimization_events")
    # project = relationship("Project", back_populates="optimization_events")
    # organization = relationship("Organization", back_populates="optimization_events")
    
    # Additional metadata
    meta_data = Column(JSON) 