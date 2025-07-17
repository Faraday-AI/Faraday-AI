"""
Feedback models for the dashboard.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.shared_base import SharedBase as Base

class Feedback(Base):
    """User feedback for GPT interactions."""
    __tablename__ = "dashboard_feedback"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("dashboard_users.id"), nullable=False)
    gpt_id = Column(String, nullable=False)
    feedback_type = Column(String, nullable=False)
    content = Column(JSON)
    rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="open")  # Added feedback status tracking
    priority = Column(String)  # Added priority tracking

    # Relationships
    user = relationship("DashboardUser", back_populates="feedback") 