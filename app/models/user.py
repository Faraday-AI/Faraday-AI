from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    last_logout = Column(DateTime, nullable=True)
    
    # ChatGPT integration fields
    chatgpt_user_id = Column(String, unique=True, nullable=True)
    chatgpt_email = Column(String, unique=True, nullable=True)
    
    # Memory recall fields
    conversation_history = Column(Text, nullable=True)  # JSON string of recent conversations
    preferences = Column(JSON, default=dict)
    custom_instructions = Column(Text, nullable=True)  # JSON string of custom instructions
    
    # Teacher-specific fields
    school = Column(String, nullable=True)
    department = Column(String, nullable=True)
    subjects = Column(Text, nullable=True)  # JSON array of subjects
    grade_levels = Column(Text, nullable=True)  # JSON array of grade levels
    
    # GPT-related fields
    gpt_roles = relationship("GPTRole", back_populates="user", cascade="all, delete-orphan")
    gpt_interactions = relationship("GPTInteraction", back_populates="user", cascade="all, delete-orphan")
    
    # Memory-related fields
    memories = relationship("UserMemory", back_populates="user", cascade="all, delete-orphan")
    memory_interactions = relationship("MemoryInteraction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>" 