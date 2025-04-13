from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.models.user import User

class UserPreferences(BaseModel):
    """User preferences and settings."""
    
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True)
    user = relationship("User", back_populates="preferences")
    theme = Column(String(50))
    notifications = Column(JSON)
    language = Column(String(50))
    timezone = Column(String(50))

class Lesson(BaseModel):
    """Lesson model for storing educational content."""
    
    __tablename__ = "lessons"
    
    title = Column(String(200), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship("User", back_populates="lessons")
    subject_category_id = Column(Integer, ForeignKey('subject_categories.id'))
    subject_category = relationship("SubjectCategory", back_populates="lessons")
    assistant_profile_id = Column(Integer, ForeignKey('assistant_profiles.id'))
    assistant_profile = relationship("AssistantProfile", back_populates="lessons")
    grade_level = Column(String(20))
    week_of = Column(Date)
    content_area = Column(String(100))
    lesson_data = Column(JSON)  # Structured lesson content
    objectives = Column(JSON)  # Learning objectives
    materials = Column(JSON)  # Required materials
    activities = Column(JSON)  # List of activities
    assessment_criteria = Column(JSON)  # Assessment criteria
    feedback = Column(JSON)  # Student feedback and ratings
    status = Column(String(50))  # draft, published, archived
    tags = Column(JSON)  # Keywords and tags
    related_lessons = Column(JSON)  # References to related lessons 