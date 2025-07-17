"""
Resource Sharing Models

This module defines models for resource sharing between users and projects.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.orm import relationship

from app.models.physical_education.base.base_class import Base
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin
from app.models.resource_management.base import ResourceType

class ResourceSharing(BaseModel, StatusMixin, MetadataMixin):
    """Model for managing resource sharing between users and projects."""
    __tablename__ = "resource_management_sharing_models"

    resource_id = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name='resource_type_enum'), nullable=False)
    
    # Sharing configuration
    sharing_type = Column(String, nullable=False)  # 'user', 'project', 'organization'
    sharing_permissions = Column(JSON, nullable=False)  # e.g., {"read": true, "write": false}
    sharing_scope = Column(String, nullable=False)  # 'public', 'private', 'restricted'
    
    # Time management
    expires_at = Column(DateTime, nullable=True)
    
    # Optional foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_with_project_id = Column(Integer, ForeignKey("dashboard_projects.id"), nullable=True)
    shared_with_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_resources")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id], back_populates="shared_resources")
    shared_with_project = relationship("DashboardProject", back_populates="shared_resources")
    shared_with_organization = relationship("Organization", back_populates="shared_resources") 