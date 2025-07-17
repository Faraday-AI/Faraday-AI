"""
Resource Optimization Models

This module defines models for resource optimization and monitoring.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum, JSON, Boolean
from sqlalchemy.orm import relationship

from app.models.physical_education.base.base_class import Base
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin
from app.models.resource_management.base import ResourceType, ResourceMetric

class ResourceOptimizationThreshold(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource optimization thresholds."""
    __tablename__ = "resource_optimization_thresholds"
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
    user = relationship("User", back_populates="resource_optimization_thresholds")

class ResourceOptimizationRecommendation(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing resource optimization recommendations."""
    __tablename__ = "resource_optimization_recommendations"
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
    user = relationship("User", back_populates="resource_optimization_recommendations")

class ResourceOptimizationEvent(BaseModel, StatusMixin, MetadataMixin):
    """Model for tracking resource optimization events and their status."""
    __tablename__ = "resource_optimization_events"
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
    user = relationship("User", back_populates="resource_optimization_events")

class ResourceEvent(BaseModel, StatusMixin, MetadataMixin):
    """Model for tracking resource events and their status."""
    __tablename__ = "resource_events"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)  # 'threshold_breach', 'optimization_applied', 'resource_shared', etc.
    severity = Column(String, nullable=False)  # 'info', 'warning', 'critical'
    
    # Resource information
    resource_id = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    metric_type = Column(Enum(ResourceMetric, name='resource_metric_enum'), nullable=False)
    
    # Event details
    details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Relationships
    user = relationship("User", back_populates="resource_events", overlaps="user")

class ResourceAlert(BaseModel, StatusMixin, MetadataMixin):
    """Model for tracking resource alerts and their status."""
    __tablename__ = "resource_alerts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    action_taken = Column(String, nullable=True)
    action_result = Column(String, nullable=True)
    resolved = Column(Boolean, default=False)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="resource_alerts", overlaps="user") 