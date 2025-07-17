"""
Database models for GPT context management.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base
from .association_tables import dashboard_context_gpts

class GPTContext(Base):
    """GPT context for managing interactions."""
    __tablename__ = "dashboard_gpt_contexts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    primary_gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    name = Column(String)
    description = Column(String)
    context_data = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("DashboardUser", back_populates="contexts")
    primary_gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition", foreign_keys=[primary_gpt_id])
    active_gpts = relationship("app.dashboard.models.gpt_models.GPTDefinition", secondary=dashboard_context_gpts)
    interactions = relationship("app.dashboard.models.context.ContextInteraction", back_populates="context")
    shared_contexts = relationship("app.dashboard.models.context.SharedContext", back_populates="context")
    summaries = relationship("app.dashboard.models.context.ContextSummary", back_populates="context")
    backups = relationship("app.dashboard.models.context.ContextBackup", back_populates="context")

    def __repr__(self):
        return f"<GPTContext {self.name}>"

class ContextInteraction(Base):
    """Interaction within a GPT context."""
    __tablename__ = "dashboard_context_interactions"

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("dashboard_gpt_contexts.id"), nullable=False)
    gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    interaction_type = Column(String, nullable=False)  # join, leave, share, update
    content = Column(JSON, default={})
    meta_data = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)

    context = relationship("app.dashboard.models.context.GPTContext", back_populates="interactions")
    gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition")

class SharedContext(Base):
    """Shared context data between GPTs."""
    __tablename__ = "dashboard_shared_contexts"

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("dashboard_gpt_contexts.id"), nullable=False)
    source_gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    target_gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    shared_data = Column(JSON, nullable=False)
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    context = relationship("app.dashboard.models.context.GPTContext", back_populates="shared_contexts")
    source_gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition", foreign_keys=[source_gpt_id])
    target_gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition", foreign_keys=[target_gpt_id])

class ContextSummary(Base):
    """Summary of a closed context."""
    __tablename__ = "dashboard_context_summaries"

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("dashboard_gpt_contexts.id"), nullable=False)
    summary = Column(JSON, nullable=False)
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    context = relationship("app.dashboard.models.context.GPTContext", back_populates="summaries")

class ContextTemplate(Base):
    """Template for creating contexts."""
    __tablename__ = "dashboard_context_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("dashboard_users.id"))

    created_by_user = relationship("DashboardUser", back_populates="context_templates")

class ContextBackup(Base):
    """Backup of a context."""
    __tablename__ = "dashboard_context_backups"

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("dashboard_gpt_contexts.id"), nullable=False)
    backup_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    context = relationship("app.dashboard.models.context.GPTContext", back_populates="backups")

class ContextMetrics(Base):
    """Performance metrics for a context."""
    __tablename__ = "dashboard_context_metrics"

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("dashboard_gpt_contexts.id"), nullable=False)
    metric_type = Column(String, nullable=False)  # performance, resource, interaction
    metric_data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    context = relationship("app.dashboard.models.context.GPTContext")

class ContextValidation(Base):
    """Validation results for a context."""
    __tablename__ = "dashboard_context_validations"

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("dashboard_gpt_contexts.id"), nullable=False)
    validation_type = Column(String, nullable=False)  # compatibility, integrity, performance, security
    is_valid = Column(Boolean, nullable=False)
    issues = Column(JSON, default=[])
    warnings = Column(JSON, default=[])
    details = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)

    context = relationship("app.dashboard.models.context.GPTContext")

class ContextOptimization(Base):
    """Optimization history for a context."""
    __tablename__ = "dashboard_context_optimizations"

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("dashboard_gpt_contexts.id"), nullable=False)
    optimization_target = Column(String, nullable=False)  # performance, efficiency, cost, reliability
    optimization_plan = Column(JSON, nullable=False)
    optimization_result = Column(JSON, nullable=False)
    metrics_before = Column(JSON, nullable=False)
    metrics_after = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    context = relationship("app.dashboard.models.context.GPTContext") 