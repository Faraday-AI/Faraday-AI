"""
Memory models for user interactions and memory management.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.models.shared_base import SharedBase

class UserMemory(SharedBase):
    """Model for storing user memories."""
    __tablename__ = "user_memories"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    importance = Column(Integer, default=0)
    category = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)

    # Relationships
    interactions = relationship("MemoryInteraction", back_populates="memory", cascade="all, delete-orphan")

class MemoryInteraction(SharedBase):
    """Model for storing interactions with memories."""
    __tablename__ = "memory_interactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey("user_memories.id"), nullable=False)
    user_id = Column(String, index=True, nullable=False)
    interaction_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    interaction_metadata = Column(JSON, nullable=True)

    # Relationships
    memory = relationship("UserMemory", back_populates="interactions")

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