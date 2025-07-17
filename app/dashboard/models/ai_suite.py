"""
AI Suite Model

This module defines the AISuite model for user's personal AI suite configuration.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

class AISuite(Base):
    """Model for AI suites."""
    __tablename__ = "ai_suites"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("DashboardUser", back_populates="ai_suites")
    tools = relationship("AITool", back_populates="suite") 