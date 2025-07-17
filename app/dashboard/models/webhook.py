"""
Webhook Model

This module defines the Webhook model for GPT webhook functionality.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

class Webhook(Base):
    """Model for webhooks."""
    __tablename__ = "webhooks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("dashboard_gpt_subscriptions.id"), nullable=False)
    url = Column(String, nullable=False)
    events = Column(JSON, nullable=True)
    secret = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("DashboardGPTSubscription", back_populates="webhooks") 