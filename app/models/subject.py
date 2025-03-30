from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

# Association table for subject categories and GPT assistants
subject_assistant = Table(
    'subject_assistant',
    BaseModel.metadata,
    Column('subject_category_id', Integer, ForeignKey('subject_categories.id')),
    Column('assistant_profile_id', Integer, ForeignKey('assistant_profiles.id'))
)

class SubjectCategory(BaseModel):
    """Top-level subject categorization."""
    
    __tablename__ = "subject_categories"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    assistants = relationship("AssistantProfile", secondary=subject_assistant, back_populates="subjects")
    lessons = relationship("Lesson", back_populates="subject_category")

class AssistantProfile(BaseModel):
    """GPT Assistant profiles for different subjects."""
    
    __tablename__ = "assistant_profiles"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    model_version = Column(String(50))
    subjects = relationship("SubjectCategory", secondary=subject_assistant, back_populates="assistants")
    lessons = relationship("Lesson", back_populates="assistant_profile")
    capabilities = relationship("AssistantCapability", back_populates="assistant_profile")
    memories = relationship("UserMemory", back_populates="assistant_profile")  # Memories created by this assistant

class AssistantCapability(BaseModel):
    """Specific capabilities of each GPT assistant."""
    
    __tablename__ = "assistant_capabilities"
    
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    assistant_profile_id = Column(Integer, ForeignKey('assistant_profiles.id'))
    assistant_profile = relationship("AssistantProfile", back_populates="capabilities") 