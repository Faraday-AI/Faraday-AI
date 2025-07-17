"""
Context Template Models

This module defines the database models for context templates
in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.mixins import StatusMixin, MetadataMixin

class ContextTemplate(SharedBase, StatusMixin, MetadataMixin):
    """Model for context templates."""
    __tablename__ = "context_templates"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)

    # Foreign Keys
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    created_by_user = relationship("User", back_populates="context_templates") 