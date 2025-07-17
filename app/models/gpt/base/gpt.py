"""
Base GPT Models

This module defines the base GPT models and related functionality.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Boolean, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

# Import association table from context models
from app.models.gpt.context.models import gpt_context_gpts

class CoreGPTDefinition(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing GPT model definitions and configurations."""
    __tablename__ = "core_gpt_definitions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)  # e.g., 'gpt-4', 'gpt-3.5-turbo'
    version = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    max_tokens = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    top_p = Column(Float, nullable=False)
    frequency_penalty = Column(Float, nullable=False)
    presence_penalty = Column(Float, nullable=False)
    
    # Capabilities and limitations
    capabilities = Column(JSON, nullable=True)  # List of supported features
    limitations = Column(JSON, nullable=True)  # List of known limitations
    context_window = Column(Integer, nullable=False)  # Maximum context length
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("organization_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    # Relationships
    user = relationship("User", back_populates="gpt_definitions")
    project = relationship("OrganizationProject", back_populates="gpt_definitions")
    organization = relationship("Organization", back_populates="core_gpt_definitions")
    integrations = relationship("app.models.gpt.integration.models.CoreGPTIntegration", back_populates="gpt_definition")
    performance_metrics = relationship("app.models.gpt.performance.models.CoreGPTPerformance", back_populates="model")
    # feedback = relationship("app.models.organization.feedback.project_feedback_management.Feedback", back_populates="gpt")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "name": self.name,
            "model_type": self.model_type,
            "version": self.version,
            "description": self.description,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "capabilities": self.capabilities,
            "limitations": self.limitations,
            "context_window": self.context_window,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        } 