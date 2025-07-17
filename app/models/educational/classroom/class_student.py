"""Models for relationships between classes and students."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship

from app.models.core.base import BaseModel, TimestampedMixin, StatusMixin
from app.models.educational.classroom.class_ import EducationalClass

class EducationalClassStudent(BaseModel, TimestampedMixin):
    """Model for student class enrollments in educational classes."""
    __tablename__ = "educational_class_students"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("educational_classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)  # active, inactive, completed
    performance_data = Column(JSON, nullable=True)
    attendance_record = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="educational_classes")
    class_ = relationship("EducationalClass", back_populates="students")

    def __repr__(self):
        return f"<EducationalClassStudent {self.class_id} - {self.student_id}>" 