"""
Message Model

This module defines the database model for educational messages in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.physical_education.base.base_class import Base

class Message(Base):
    """Model for managing educational messages."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    content = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    status = Column(String)  # sent, delivered, read

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id]) 