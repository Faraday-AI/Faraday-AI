"""
Context Models

This module defines the context-related models.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, JSON, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.core.base import BaseModel, StatusMixin, MetadataMixin, TimestampedMixin
from app.models.gpt.context.types import ContextType, InteractionType, SharingType, SharingScope

# Association table for contexts and GPTs
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.shared_base import SharedBase

gpt_context_gpts = Table(
    'gpt_context_gpts',
    SharedBase.metadata,
    Column('context_id', Integer, ForeignKey('gpt_interaction_contexts.id')),
    Column('gpt_id', Integer, ForeignKey('gpt_definitions.id'))
)

class GPTContext(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for managing GPT interaction contexts."""
    __tablename__ = "gpt_interaction_contexts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    primary_gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    context_type = Column(Enum(ContextType), nullable=False)
    context_data = Column(JSON)
    max_tokens = Column(Integer, nullable=True)
    token_count = Column(Integer, default=0)
    priority = Column(Integer, default=0)
    closed_at = Column(DateTime)
    settings = Column(JSON, nullable=True)
    context_metadata = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="gpt_contexts")
    primary_gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition")
    active_gpts = relationship(
        "app.dashboard.models.gpt_models.GPTDefinition",
        secondary=gpt_context_gpts
    )
    interactions = relationship("app.models.gpt.context.models.ContextInteraction", back_populates="context")
    shared_instances = relationship("app.models.gpt.context.models.SharedContext", back_populates="context")
    summaries = relationship("app.models.gpt.context.models.ContextSummary", back_populates="context")
    backups = relationship("app.models.gpt.context.models.ContextBackup", back_populates="context")
    context_data_items = relationship("app.models.gpt.context.models.ContextData", back_populates="context")
    context_metrics = relationship("app.models.gpt.context.models.ContextMetrics", back_populates="context")
    context_sharing = relationship("app.models.gpt.context.models.ContextSharing", back_populates="context")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "user_id": self.user_id,
            "primary_gpt_id": self.primary_gpt_id,
            "name": self.name,
            "description": self.description,
            "context_type": self.context_type.value if self.context_type else None,
            "context_data": self.context_data,
            "max_tokens": self.max_tokens,
            "token_count": self.token_count,
            "priority": self.priority,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }

class ContextInteraction(BaseModel, MetadataMixin):
    """Model for tracking interactions within a context."""
    __tablename__ = "gpt_context_interactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_interaction_contexts.id"), nullable=False)
    gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    content = Column(JSON)
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system', etc.
    token_count = Column(Integer, nullable=False)
    processing_time = Column(Float, nullable=True)  # in milliseconds
    processed_at = Column(DateTime, nullable=True)

    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    context = relationship("app.models.gpt.context.models.GPTContext", back_populates="interactions")
    gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition")
    user = relationship("User", back_populates="context_interactions")
    project = relationship("app.dashboard.models.project.DashboardProject", back_populates="context_interactions")
    organization = relationship("Organization", back_populates="context_interactions")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "context_id": self.context_id,
            "gpt_id": self.gpt_id,
            "interaction_type": self.interaction_type.value if self.interaction_type else None,
            "content": self.content,
            "role": self.role,
            "token_count": self.token_count,
            "processing_time": self.processing_time,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        }

class SharedContext(BaseModel, StatusMixin, MetadataMixin):
    """Model for managing shared GPT contexts."""
    __tablename__ = "shared_contexts"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_interaction_contexts.id"), nullable=False)
    sharing_type = Column(Enum(SharingType), nullable=False)
    sharing_permissions = Column(JSON, nullable=False)
    sharing_scope = Column(Enum(SharingScope), nullable=False)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_with_project_id = Column(Integer, ForeignKey("dashboard_projects.id"), nullable=True)
    shared_with_organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    # Relationships
    context = relationship("app.models.gpt.context.models.GPTContext", back_populates="shared_instances")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_shared_contexts")
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id], back_populates="shared_contexts")
    shared_with_project = relationship("app.dashboard.models.project.DashboardProject", back_populates="shared_contexts")
    shared_with_organization = relationship("Organization", back_populates="shared_contexts")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "context_id": self.context_id,
            "sharing_type": self.sharing_type.value if self.sharing_type else None,
            "sharing_permissions": self.sharing_permissions,
            "sharing_scope": self.sharing_scope.value if self.sharing_scope else None,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "owner_id": self.owner_id,
            "shared_with_user_id": self.shared_with_user_id,
            "shared_with_project_id": self.shared_with_project_id,
            "shared_with_organization_id": self.shared_with_organization_id
        }

class ContextSummary(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for storing context summaries."""
    __tablename__ = "gpt_context_summaries"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_interaction_contexts.id"), nullable=False)
    summary = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=True)
    sentiment = Column(String, nullable=True)
    topics = Column(JSON, nullable=True)
    token_count = Column(Integer, nullable=False)
    summary_type = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=True)
    summary_metadata = Column(JSON, nullable=True)

    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    context = relationship("app.models.gpt.context.models.GPTContext", back_populates="summaries")
    user = relationship("User", back_populates="context_summaries")
    project = relationship("app.dashboard.models.project.DashboardProject", back_populates="context_summaries")
    organization = relationship("Organization", back_populates="context_summaries")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "context_id": self.context_id,
            "summary": self.summary,
            "key_points": self.key_points,
            "sentiment": self.sentiment,
            "topics": self.topics,
            "token_count": self.token_count,
            "summary_type": self.summary_type,
            "confidence_score": self.confidence_score,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        }

class ContextBackup(BaseModel, StatusMixin, MetadataMixin):
    """Model for storing context backups."""
    __tablename__ = "gpt_context_backups"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_interaction_contexts.id"), nullable=False)
    backup_content = Column(JSON, nullable=False)
    backup_type = Column(String, nullable=False)
    backup_reason = Column(String, nullable=True)
    backup_metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    is_restored = Column(Boolean, default=False)
    restored_at = Column(DateTime, nullable=True)

    # Optional foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    context = relationship("app.models.gpt.context.models.GPTContext", back_populates="backups")
    user = relationship("User", back_populates="context_backups")
    project = relationship("app.dashboard.models.project.DashboardProject", back_populates="context_backups")
    organization = relationship("Organization", back_populates="context_backups")

    def dict(self):
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "context_id": self.context_id,
            "backup_content": self.backup_content,
            "backup_type": self.backup_type,
            "backup_reason": self.backup_reason,
            "backup_metadata": self.backup_metadata,
            "error_message": self.error_message,
            "is_restored": self.is_restored,
            "restored_at": self.restored_at.isoformat() if self.restored_at else None,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "organization_id": self.organization_id
        }

class ContextData(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for context data."""
    __tablename__ = "context_data"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_interaction_contexts.id"), nullable=False)
    gpt_id = Column(Integer, ForeignKey("gpt_definitions.id"), nullable=False)
    data_type = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    data_metadata = Column(JSON, nullable=True)

    # Relationships
    context = relationship("app.models.gpt.context.models.GPTContext", back_populates="context_data_items")
    gpt = relationship("app.dashboard.models.gpt_models.GPTDefinition", back_populates="context_data")

class ContextMetrics(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for context metrics."""
    __tablename__ = "gpt_context_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_interaction_contexts.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    metric_metadata = Column(JSON, nullable=True)

    # Relationships
    context = relationship("app.models.gpt.context.models.GPTContext", back_populates="context_metrics")

class ContextSharing(BaseModel, TimestampedMixin, StatusMixin, MetadataMixin):
    """Model for context sharing."""
    __tablename__ = "gpt_context_sharing"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_interaction_contexts.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permissions = Column(JSON, nullable=True)
    sharing_metadata = Column(JSON, nullable=True)

    # Relationships
    context = relationship("app.models.gpt.context.models.GPTContext", back_populates="context_sharing")
    shared_with_user = relationship("User", back_populates="context_sharing_instances") 