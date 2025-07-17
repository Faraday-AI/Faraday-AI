"""
Context Shared Models

This module defines models for shared GPT contexts.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.shared_base import SharedBase
from app.models.mixins import MetadataMixin

class ContextSharing(SharedBase, MetadataMixin):
    """Model for context sharing."""
    __tablename__ = "context_sharing"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    context_id = Column(Integer, ForeignKey("gpt_contexts.id"), nullable=False)
    source_gpt_id = Column(Integer, ForeignKey("core_gpt_definitions.id"), nullable=False)
    target_gpt_id = Column(Integer, ForeignKey("core_gpt_definitions.id"), nullable=False)
    sharing_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sharing_metadata = Column(JSON, nullable=True)

    # Relationships
    context = relationship("GPTContext", back_populates="sharing")
    source_gpt = relationship("app.models.gpt.base.gpt.GPTDefinition", foreign_keys=[source_gpt_id], back_populates="source_sharing")
    target_gpt = relationship("app.models.gpt.base.gpt.GPTDefinition", foreign_keys=[target_gpt_id], back_populates="target_sharing") 