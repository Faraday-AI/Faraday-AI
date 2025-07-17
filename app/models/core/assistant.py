from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.core.base import CoreBase
from .base import BaseModel

# Association table for many-to-many relationship between AssistantProfile and SubjectCategory
subject_assistant = Table(
    'subject_assistant',
    CoreBase.metadata,
    Column('subject_category_id', Integer, ForeignKey('subject_categories.id')),
    Column('assistant_profile_id', Integer, ForeignKey('assistant_profiles.id'))
)

class AssistantProfile(BaseModel):
    """Model for GPT assistant configuration and management."""
    
    __tablename__ = "assistant_profiles"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String)
    model_version = Column(String(50), nullable=False)
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    max_context_length = Column(Integer, default=4096)
    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=1.0)
    frequency_penalty = Column(Float, default=0.0)
    presence_penalty = Column(Float, default=0.0)
    stop_sequences = Column(JSON)  # Changed from ARRAY(String) to JSON
    assistant_metadata = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved name
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string references to avoid circular imports
    memories = relationship("app.models.core.memory.UserMemory", back_populates="assistant_profile")
    capabilities = relationship("AssistantCapability", back_populates="assistant_profile")
    lessons = relationship("app.models.core.lesson.Lesson", back_populates="assistant_profile")
    subject_categories = relationship("app.models.core.subject.SubjectCategory", 
                                    secondary=subject_assistant, 
                                    back_populates="assistant_profiles")

class AssistantCapability(BaseModel):
    """Model for specific abilities of each GPT assistant."""
    
    __tablename__ = "assistant_capabilities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String)
    assistant_profile_id = Column(Integer, ForeignKey('assistant_profiles.id', ondelete='CASCADE'))
    parameters = Column(JSON)
    is_enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    version = Column(String(20))
    capability_metadata = Column(JSON)  # Renamed from metadata to avoid SQLAlchemy reserved name
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assistant_profile = relationship("AssistantProfile", back_populates="capabilities")
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    ) 