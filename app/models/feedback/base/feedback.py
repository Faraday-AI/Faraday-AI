"""
Feedback Model

This module defines the database model for user feedback in the Faraday AI system.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin

class Feedback(BaseModel, StatusMixin, MetadataMixin):
    """Model for user feedback on GPT interactions."""
    __tablename__ = "feedback"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    feedback_type = Column(String, nullable=False)
    content = Column(JSON, nullable=True)
    rating = Column(Integer, nullable=True)
    priority = Column(String, nullable=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    gpt_id = Column(Integer, ForeignKey("core_gpt_definitions.id"))

    # Relationships
    user = relationship("User", back_populates="feedback") 