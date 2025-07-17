"""
Marketplace Listing Model

This module defines the MarketplaceListing model for tool listings in the marketplace.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Numeric

from app.models.shared_base import SharedBase as Base

class MarketplaceListing(Base):
    """Model for tool listings in the marketplace."""
    __tablename__ = "dashboard_marketplace_listings"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    tool_id = Column(Integer, ForeignKey("ai_tools.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    features = Column(JSON)
    pricing_details = Column(JSON)
    category = Column(String)
    tags = Column(JSON)
    preview_url = Column(String)
    documentation_url = Column(String)
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tool = relationship("AITool", back_populates="marketplace_listing") 