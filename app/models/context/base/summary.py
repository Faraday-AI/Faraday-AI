"""
Context Summary and Backup Models

This module defines the database models for context summaries and backups
in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.mixins import StatusMixin, MetadataMixin

class ContextSummary(SharedBase, StatusMixin, MetadataMixin):
    """Model for context summaries."""
    __tablename__ = "context_summaries"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    summary_type = Column(String, nullable=False)  # closure, checkpoint, etc.
    content = Column(JSON, nullable=False)

    # Foreign Keys
    context_id = Column(Integer, ForeignKey("gpt_contexts.id"))

    # Relationships
    context = relationship("GPTContext", back_populates="summaries")

class ContextBackup(SharedBase, StatusMixin, MetadataMixin):
    """Model for context backups."""
    __tablename__ = "context_backups"
    __table_args__ = {'extend_existing': True}

    backup_data = Column(JSON, nullable=False)

    # Foreign Keys
    context_id = Column(Integer, ForeignKey("gpt_contexts.id"))

    # Relationships
    context = relationship("GPTContext", back_populates="backups") 