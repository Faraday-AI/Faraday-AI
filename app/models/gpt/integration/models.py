"""
Integration Models

This module defines the integration-related models.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, JSON, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class CoreGPTIntegration(BaseModel, StatusMixin, MetadataMixin):
    """Model for GPT integrations with external services and platforms."""
    __tablename__ = "gpt_integrations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    gpt_id = Column(Integer, ForeignKey("core_gpt_definitions.id"), nullable=False)
    integration_type = Column(String, nullable=False)  # e.g., "api", "webhook", "database"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Integration configuration
    configuration = Column(JSON, nullable=False, default={})
    credentials = Column(JSON, nullable=True)  # Encrypted credentials
    endpoint_url = Column(String, nullable=True)
    headers = Column(JSON, nullable=True)
    
    # Integration state
    is_healthy = Column(Boolean, default=True)
    last_check = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("organization_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Relationships
    gpt_definition = relationship("app.models.gpt.base.gpt.CoreGPTDefinition", back_populates="integrations")
    user = relationship("User", back_populates="gpt_integrations")
    project = relationship("OrganizationProject", back_populates="gpt_integrations")
    organization = relationship("Organization", back_populates="core_gpt_integrations")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "gpt_id": self.gpt_id,
            "integration_type": self.integration_type,
            "name": self.name,
            "description": self.description,
            "configuration": self.configuration,
            "credentials": self.credentials,
            "endpoint_url": self.endpoint_url,
            "headers": self.headers,
            "is_healthy": self.is_healthy,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_message": self.error_message,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        } 