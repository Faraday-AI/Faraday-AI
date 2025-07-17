"""
Category Model

This module defines the Category model for GPT categories.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Table, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

# Association table for GPT categories
gpt_categories = Table(
    "gpt_categories",
    Base.metadata,
    Column("gpt_id", Integer, ForeignKey("dashboard_gpt_subscriptions.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("dashboard_categories.id"), primary_key=True),
    extend_existing=True
)

class Category(Base):
    """Model for GPT categories."""
    __tablename__ = "dashboard_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    gpts = relationship("DashboardGPTSubscription", secondary="gpt_categories", back_populates="categories") 