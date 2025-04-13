from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Text, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from pydantic import BaseModel as PydanticBaseModel
from datetime import datetime
from typing import Optional, Dict, List
import uuid

class UserMemoryResponse(PydanticBaseModel):
    """Pydantic model for UserMemory responses."""
    id: int
    user_id: uuid.UUID
    assistant_profile_id: int
    content: str
    context: Optional[Dict] = None
    importance: float = 1.0
    last_accessed: Optional[datetime] = None
    category: str
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    confidence: Optional[float] = None
    version: Optional[str] = None

    class Config:
        from_attributes = True

class MemoryInteractionResponse(PydanticBaseModel):
    """Pydantic model for MemoryInteraction responses."""
    id: int
    memory_id: int
    user_id: uuid.UUID
    interaction_type: str
    timestamp: datetime
    context: Optional[Dict] = None
    feedback: Optional[Dict] = None

    class Config:
        from_attributes = True

class UserMemory(BaseModel):
    """Model for storing user-specific memory data for GPT assistants."""
    
    __tablename__ = "user_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship("User", back_populates="memories")
    assistant_profile_id = Column(Integer, ForeignKey('assistant_profiles.id'))
    assistant_profile = relationship("AssistantProfile", back_populates="memories")
    
    # Memory content
    content = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context about the memory
    importance = Column(Float, default=1.0)  # Importance score (0-1)
    last_accessed = Column(DateTime)  # When this memory was last used
    
    # Memory categorization
    category = Column(String(100))  # e.g., "preferences", "history", "achievements"
    tags = Column(JSON)  # Keywords for better retrieval
    
    # Memory metadata
    source = Column(String(100))  # Where this memory came from
    confidence = Column(Float)  # Confidence in the memory's accuracy
    version = Column(String(50))  # Version of the GPT that created this memory

class MemoryInteraction(BaseModel):
    """Model for tracking how memories are used and updated."""
    
    __tablename__ = "memory_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey('user_memories.id'))
    memory = relationship("UserMemory")
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship("User")
    
    # Interaction details
    interaction_type = Column(String(50))  # e.g., "read", "update", "delete"
    timestamp = Column(DateTime)
    context = Column(JSON)  # Context of the interaction
    feedback = Column(JSON)  # User feedback on memory usefulness 