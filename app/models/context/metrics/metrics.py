"""
Context Metrics Models

This module defines the database models for context performance metrics,
validation, and optimization in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.shared_base import SharedBase
from app.models.mixins import StatusMixin, MetadataMixin

class ContextMetrics(SharedBase, StatusMixin, MetadataMixin):
    """Model for context performance metrics."""
    __tablename__ = "context_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    metric_type = Column(String, nullable=False)  # performance, resource, interaction
    metric_data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Foreign Keys
    context_id = Column(Integer, ForeignKey("gpt_contexts.id"))

    # Relationships
    context = relationship("GPTContext", back_populates="metrics")

class ContextValidation(SharedBase, StatusMixin, MetadataMixin):
    """Model for context validation results."""
    __tablename__ = "context_validations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    validation_type = Column(String, nullable=False)  # compatibility, integrity, performance, security
    is_valid = Column(Boolean, nullable=False)
    issues = Column(JSON, default=[])
    warnings = Column(JSON, default=[])
    details = Column(JSON, default={})
    timestamp = Column(DateTime, nullable=False)

    # Foreign Keys
    context_id = Column(Integer, ForeignKey("gpt_contexts.id"))

    # Relationships
    context = relationship("GPTContext", back_populates="validations")

class ContextOptimization(SharedBase, StatusMixin, MetadataMixin):
    """Model for context optimization history."""
    __tablename__ = "context_optimizations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    optimization_target = Column(String, nullable=False)  # performance, efficiency, cost, reliability
    optimization_plan = Column(JSON, nullable=False)
    optimization_result = Column(JSON, nullable=False)
    metrics_before = Column(JSON, nullable=False)
    metrics_after = Column(JSON, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Foreign Keys
    context_id = Column(Integer, ForeignKey("gpt_contexts.id"))

    # Relationships
    context = relationship("GPTContext", back_populates="optimizations") 