from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class Lesson(BaseModel):
    """Model for educational content management."""
    
    __tablename__ = "lessons"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    subject_category_id = Column(Integer, ForeignKey('subject_categories.id'))
    assistant_profile_id = Column(Integer, ForeignKey('assistant_profiles.id'))
    grade_level = Column(String(20))
    week_of = Column(Date)
    content_area = Column(String(100))
    content = Column(Text, nullable=True)
    lesson_data = Column(JSON)
    objectives = Column(JSON)
    materials = Column(JSON)
    activities = Column(JSON)
    assessment_criteria = Column(JSON)
    feedback = Column(JSON)
    status = Column(String(50), default='draft')
    version = Column(Integer, nullable=True, default=1)
    tags = Column(JSON)
    related_lessons = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string references to avoid circular imports
    user = relationship("User", back_populates="lessons", lazy="joined")
    subject_category = relationship("SubjectCategory", back_populates="lessons", lazy="joined")
    assistant_profile = relationship("AssistantProfile", back_populates="lessons", lazy="joined")
    
    def __repr__(self):
        return f"<Lesson {self.title}>"

    __table_args__ = (
        {'sqlite_autoincrement': True},
    ) 