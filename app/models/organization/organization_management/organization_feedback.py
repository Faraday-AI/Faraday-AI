"""
Organization Feedback Model

This model represents feedback for organizations.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Integer as SQLInteger, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class OrganizationFeedback(Base):
    """Model for organization feedback."""
    __tablename__ = "organization_feedback"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback_type = Column(String(50), nullable=False)  # Suggestion, Complaint, Compliment, Question, Report
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    rating = Column(SQLInteger, nullable=True)  # 1-5 scale
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="feedback_records")
    user = relationship("User", back_populates="organization_feedback")

    def __repr__(self):
        return f"<OrganizationFeedback(id={self.id}, type={self.feedback_type}, rating={self.rating})>"