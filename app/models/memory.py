"""
Memory models for user interactions and memory management.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.shared_base import SharedBase
from app.models.core.user import User

class SimpleUserMemory(SharedBase):
    """Model for storing user memories."""
    __tablename__ = "simple_user_memories"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    assistant_profile_id = Column(Integer, ForeignKey("assistant_profiles.id"), nullable=True)
    content = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    importance = Column(Integer, default=0)
    category = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    source = Column(String, nullable=True)
    confidence = Column(Integer, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow)

    # Relationships
    simple_user = relationship("User")
    interactions = relationship("SimpleMemoryInteraction", back_populates="memory", cascade="all, delete-orphan")

class SimpleMemoryInteraction(SharedBase):
    """Model for storing interactions with memories."""
    __tablename__ = "simple_memory_interactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey("simple_user_memories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    interaction_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    interaction_metadata = Column(JSON, nullable=True)

    # Relationships
    memory = relationship("SimpleUserMemory", back_populates="interactions")
    user = relationship("User")

# Pydantic models for API responses
class UserMemoryResponse(BaseModel):
    """Response model for user memories."""
    id: int
    user_id: str
    content: str
    context: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    importance: int
    category: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True

class MemoryInteractionResponse(BaseModel):
    """Response model for memory interactions."""
    id: int
    memory_id: int
    user_id: str
    interaction_type: str
    content: Optional[str] = None
    created_at: datetime
    interaction_metadata: Optional[dict] = None

    class Config:
        from_attributes = True 