"""
Message Board Models

This module defines the database models for educational message boards in the Faraday AI system.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.shared_base import SharedBase as Base

class MessageBoard(Base):
    """Model for managing educational message boards."""
    __tablename__ = "message_boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User")
    course = relationship("Course")
    posts = relationship("MessageBoardPost", overlaps="posts")

class MessageBoardPost(Base):
    """Model for managing message board posts."""
    __tablename__ = "message_board_posts"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("message_boards.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String)  # active, archived, deleted

    # Relationships
    board = relationship("MessageBoard", overlaps="posts")
    author = relationship("User") 