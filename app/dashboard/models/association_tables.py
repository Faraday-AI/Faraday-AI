"""
Association tables for the dashboard models.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, Table
from datetime import datetime

from app.models.shared_base import SharedBase as Base

# Association table for GPT sharing
gpt_sharing = Table(
    'gpt_sharing',
    Base.metadata,
    Column('subscription_id', Integer, ForeignKey('dashboard_gpt_subscriptions.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey("users.id"), primary_key=True),
    Column('permissions', JSON),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('expires_at', DateTime),
    extend_existing=True
)

# Association table for GPTs in a context
dashboard_context_gpts = Table(
    "dashboard_context_gpts",
    Base.metadata,
    Column("context_id", Integer, ForeignKey("dashboard_gpt_contexts.id")),
    Column("gpt_id", Integer, ForeignKey("gpt_definitions.id")),
    extend_existing=True
) 