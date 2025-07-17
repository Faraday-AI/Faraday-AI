"""
GPT Version Model

This module defines the GPTVersion model for version control of GPT subscriptions.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

class GPTVersion(Base):
    """Model for GPT versions."""
    __tablename__ = "gpt_versions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("dashboard_gpt_subscriptions.id"), nullable=False)
    version = Column(String, nullable=False)
    status = Column(String, nullable=False)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)

    # Relationships
    subscription = relationship("DashboardGPTSubscription", back_populates="versions") 