from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid

class GPTRole(Base):
    """Model for tracking user's GPT roles and preferences."""
    __tablename__ = 'gpt_roles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    gpt_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_accessed = Column(DateTime(timezone=True))
    preferences = Column(JSON)
    
    user = relationship("User", back_populates="gpt_roles")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'gpt_name', name='uix_user_gpt'),
    )

class GPTInteraction(Base):
    """Model for tracking interactions between users, GPTs, and memories."""
    __tablename__ = 'gpt_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    gpt_name = Column(String(255), nullable=False)
    memory_id = Column(Integer, ForeignKey('user_memories.id'))
    interaction_type = Column(String(50))
    interaction_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    user = relationship("User", back_populates="gpt_interactions")
    memory = relationship("UserMemory", back_populates="interactions") 