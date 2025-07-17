from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Text, Float, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
from .assistant import AssistantProfile
from pydantic import BaseModel as PydanticBaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, List

class UserMemoryResponse(PydanticBaseModel):
    """Pydantic model for UserMemory responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
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

class MemoryInteractionResponse(PydanticBaseModel):
    """Pydantic model for MemoryInteraction responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    memory_id: int
    user_id: int
    interaction_type: str
    timestamp: datetime
    context: Optional[Dict] = None
    feedback: Optional[Dict] = None

class UserMemory(BaseModel):
    """Model for storing user-specific memory data for GPT assistants."""
    
    __tablename__ = "user_memories"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship("app.models.core.user.User", back_populates="memories")
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MemoryInteraction(BaseModel):
    """Model for tracking how memories are used and updated."""
    
    __tablename__ = "memory_interactions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey('user_memories.id'))
    memory = relationship("UserMemory")
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("app.models.core.user.User")
    
    # Interaction details
    interaction_type = Column(String(50))  # e.g., "read", "update", "delete"
    timestamp = Column(DateTime)
    context = Column(JSON)  # Context of the interaction
    feedback = Column(JSON)  # User feedback on memory usefulness
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 