"""
Context Models

This module defines the database models for managing GPT contexts
and coordination in the Faraday AI Dashboard.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Table, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

from app.dashboard.models.context import (
    GPTContext,
    ContextInteraction,
    SharedContext,
    ContextSummary,
    ContextTemplate,
    ContextBackup,
    ContextMetrics,
    ContextValidation,
    ContextOptimization
)

# Re-export the classes
__all__ = [
    'GPTContext',
    'ContextInteraction',
    'SharedContext',
    'ContextSummary',
    'ContextTemplate',
    'ContextBackup',
    'ContextMetrics',
    'ContextValidation',
    'ContextOptimization'
]

# Remove duplicate table definition - using the one from context.py
# context_gpts = Table(
#     'context_gpts',
#     Base.metadata,
#     Column('context_id', Integer, ForeignKey('gpt_contexts.id')),
#     Column('gpt_definition_id', Integer, ForeignKey('gpt_definitions.id'))
# )

# Remove duplicate model definitions
# class ContextInteraction(Base):
# class SharedContext(Base):
# class ContextSummary(Base): 