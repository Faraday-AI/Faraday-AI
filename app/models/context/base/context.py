"""
Base Context Models

This module defines the core database models for GPT context management
and interactions in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.mixins import StatusMixin, MetadataMixin

# Association table for GPTs in a context
context_gpts = Table(
    "context_gpts",
    SharedBase.metadata,
    Column("context_id", Integer, ForeignKey("gpt_contexts.id")),
    Column("gpt_id", Integer, ForeignKey("gpt_definitions.id")),
    extend_existing=True
)

class GPTContext(SharedBase, StatusMixin, MetadataMixin):
    """Model for GPT context management."""
    __tablename__ = "gpt_contexts"
    __table_args__ = {'extend_existing': True}

    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    context_data = Column(JSON, default={})
    closed_at = Column(DateTime, nullable=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    primary_gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"))

    # Relationships
    user = relationship("User", back_populates="contexts")
    primary_gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition", foreign_keys=[primary_gpt_id])
    active_gpts = relationship("app.dashboard.models.gpt_models.GPTDefinition", secondary=context_gpts)
    interactions = relationship("app.models.context.base.context.ContextInteraction", back_populates="context")
    summaries = relationship("ContextSummary", back_populates="context")
    backups = relationship("ContextBackup", back_populates="context")
    metrics = relationship("ContextMetrics", back_populates="context")
    validations = relationship("ContextValidation", back_populates="context")
    optimizations = relationship("ContextOptimization", back_populates="context")

class ContextInteraction(SharedBase, StatusMixin, MetadataMixin):
    """Model for context interactions."""
    __tablename__ = "context_interactions"
    __table_args__ = {'extend_existing': True}

    interaction_type = Column(String, nullable=False)  # query, response, action, etc.
    content = Column(JSON, default={})
    timestamp = Column(DateTime, nullable=False)

    # Foreign Keys
    context_id = Column(Integer, ForeignKey("gpt_contexts.id"))
    gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"))

    # Relationships
    context = relationship("app.models.context.base.context.GPTContext", back_populates="interactions")
    gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition") 