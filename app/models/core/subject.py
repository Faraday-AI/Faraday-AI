from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class SubjectCategory(BaseModel):
    """Model for subject area organization."""
    
    __tablename__ = "subject_categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    level = Column(String)  # For hierarchical structure
    path = Column(String)  # For hierarchical structure
    category_data = Column(JSON)
    
    # Relationships - using string references to avoid circular imports
    lessons = relationship("app.models.core.lesson.Lesson", back_populates="subject_category")
    assistant_profiles = relationship("app.models.core.assistant.AssistantProfile", 
                                    secondary="subject_assistant", 
                                    back_populates="subject_categories")
    
    __table_args__ = (
        {'sqlite_autoincrement': True},
    ) 