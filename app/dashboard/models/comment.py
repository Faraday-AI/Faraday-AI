"""
Comment Model

This module defines the Comment model for project comments functionality.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

class Comment(Base):
    """Model for project comments."""
    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("dashboard_projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("DashboardProject", back_populates="comments")
    user = relationship("DashboardUser", back_populates="comments") 